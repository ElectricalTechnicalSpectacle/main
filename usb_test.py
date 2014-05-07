#!/usr/bin/python
#
# Created by: Jacob Branaugh
# Created on: 02/02/2014 22:40
#
# Program to implement usb transfer between beaglebone and stmicro
#

import sys
import usb.core
import subprocess
import select
import socket
import threading
import signal
import random
import getpass
import math
import usb_header #for current lookup table


#Global socket data write buffer
socket_buffer = []

#global lookup table for current value matchings
current_lookup = usb_header.lookup_table


#################################################################################
###################### SOCKET STUFF #############################################
#################################################################################
PORT =      59481
HOST =      '127.0.0.1'
BACKLOG =   5
BUFF =      2048

def get_buffer():
	global socket_buffer
	return socket_buffer

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.host = HOST
        self.port = PORT
        self.conn = (self.host, self.port)
        self.backlog = BACKLOG
        self.server = None
        self.threads = []
        self.clients = [] 
    def register_signals(self):
        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGQUIT, self.signal_handler)

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.conn)
            self.server.listen(self.backlog)
            print "Started server: " + str(self.host) + " on port: " + str(self.port)
            print "Listening for incoming connections..."
        except socket.error as message:
            if self.server:
                self.server.close()
            print >> sys.stderr, "Could not open socket: " + str(message)
            sys.exit(1)
        #self.register_signals()

    def signal_handler(self, signum, frame):
        print "Caught signal: ", signum
        print "Closing the socket and cleaning up the mess..."
        self.server_shutdown()

    def server_shutdown(self):
        self.running = 0
        for c in self.threads:
            try:
                c.join()
            except RuntimeError:
                pass
        if self.server:
            self.server.close()
        sys.exit(1)

    def run(self):
	global socket_buffer
        self.open_socket()
        inputs = [self.server, sys.stdin]
        self.running = 1
        while self.running:
            try:
                iready, oready, eready = select.select(inputs, [], [])
            except select.error, err:
                self.running = 0
                pass
            for s in iready:
                if s == self.server:
                    try:
                        c = Client(self, self.server.accept())
                        c.start()
                        self.threads.append(c)
                    except socket.error, err:
                        pass

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    self.running = 0 

                else:
                    self.running = 0

        # close all threads
        print 'Closing....'
        for c in self.threads:
            c.join()
        self.server_shutdown()


class Client(threading.Thread):
    def __init__(self, server, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.server = server

    def run(self):
	global socket_buffer
	send_str = ""
    	print "Incoming connection from : " + str(self.address)
        running = 1
        while running:
            data = self.client.recv(BUFF)
            if data:
                if data == 'Hello':
                    self.client.send("Hello back")

                elif data == 'Test':
                    num_1 = str(random.randint(1, 99999))
                    num_2 = str(random.randint(1, 99)).rjust(2, '0')
                    unit = random.choice(['mW', 'W', 'KW', 'MW']);
                    full =  "|".join([num_1, num_2, unit])
                    self.client.send(full)
                    
                elif data == 'get':
			#socket_buffer_tmp = get_buffer()
			#print socket_buffer_tmp
			#if len(socket_buffer_tmp) == 0:
			#	self.client.send("empty")
			#else:
			#	send_str = str(len(socket_buffer_tmp)) + "|"
			#	for item in socket_buffer_tmp:
			#		send_str += item
			#	self.client.send(send_str[:-1])
			#	socket_buffer = []
			#print socket_buffer
			if len(socket_buffer) == 0:
				self.client.send("empty")
			else:
				send_str = str(len(socket_buffer)) + "|"
				for item in socket_buffer:
					send_str += item
				print send_str[:4]
				self.client.send(send_str[:-1])
				#self.client.send("empty")
				socket_buffer = []

				send_str = ""
                elif data == 'Done':
                    self.server.server_shutdown()
                    running = 0
            else:
                running = 0
        
        self.client.close()
    
    def __repr__(self):
        return str(self.address)
##############################################################################
##############################################################################
##############################################################################

def convert_current(num):
	#return (num/65535.0)*1000
	return (2.319*(math.e**((-.7434)*num*7.6295*(10**(-5))))/2.5)*1000


# Data key for wired mouse:
# 
# |       0       |    1     |    2     |    3     |       4       |      5     |
# | button clicks | movement | movement | movement | wheel scrolls | wheel tilt |
#
# Data key for power info from STmicro
#                                                               |            Repeat However Many              |
# |      1 Byte       |     1 Byte      |  1 Byte   |  1 Byte   |   2 Byte    |   2 Byte    |     1 Byte      |
# |   Packet Length   |   Packet Type   |   Sum 1   |   Sum 2   |   Voltage   |   Current   |   Power State   |
#
def process_raw(packet):
	#Local variables
	NACK = 1
	global socket_buffer
	global current_lookup

	#try:
	length = int(packet[0])
	num_readings = (length - 4) / 5
	pkt_type = int(packet[1])
	if pkt_type == NACK:
		#Handle nack appropriately 
		print "Packet was a NACK"
		return

	check_1 = int(packet[2])	#Checksums not needed, only here to keep the
	check_2 = int(packet[3])	#numbers in order

	#string = str(num_readings) + "|"
	string = ""
	for i in range(0, num_readings):
		#parse raw fields
		idx = i * 5 + 4
		current = ((int(packet[idx+1]) << 8) | int(packet[idx]))
		voltage = ((int(packet[idx+3]) << 8) | int(packet[idx+2]))
		pwr_state = int(packet[idx+4])

		#convert raw data
		v_conv = (voltage/65200.0)*12.0
		i_conv = current_lookup[current] - 2
		power = v_conv * i_conv

		#account for sense resistor voltage drop
		if (i_conv > 500):
			v_conv -= 0.05
		elif (i_conv > 100 and i_conv <= 500):
			v_conv -= 0.025
		elif (i_conv <= 100):
			v_conv -= 0.0125
		
		if (v_conv < 6):
			v_conv -= 0.01

		v_conv -= 0.05

		#build the string
		string = string + \
			 str(int(v_conv)) + "," + \
			 str(v_conv-int(v_conv))[2:4] + "," + \
			 "V" + "&" + \
			 str(int(i_conv)) + "," + \
			 str(i_conv-int(i_conv))[2:4] + "," + \
			 "mA" + "&" + \
			 str(int(power)) + "," + \
			 str(power-int(power))[2:4] + "," + \
			 "mW" + "&" + \
			 str(pwr_state) + "~"
			 #"mW" + "~" 		
			 
		#test print
		#print "Packet Length:    " + str(length) + "\n" + \
		#      "Number Values:    " + str(num_readings) + "\n" + \
		#      "Packet Type:      " + str(pkt_type) + "\n" + \
		#      "Checksum 1:       " + str(check_1) + "\n" + \
		#      "Checksum 2:       " + str(check_2) + "\n" + \
		#      "Current Reading:  " + str(i_conv) + "\n" + \
		#      "Voltage Reading:  " + str(v_conv) + "\n" + \
		#      "Power Reading:    " + str(power) + "\n" + \
		#      "DUT Power State:  " + str(pwr_state) + "\n"
	#except:
	#	print "Error: Invalid Packet"

	print string
	socket_buffer.append(string)		 


def usb_init(wr_ep, rd_ep):
	send_data = b'\x04\x0c\x00\x00' #read one

	# do two reads to throw away inital garbage packets
	for i in range(0,2):
		try:
			wr_ep.write(send_data)
		except usb.core.USBError as e:
			raise ValueError("Couldn't Write To Device In Init: %s" % str(e))

		try:
			data = rd_ep.read(4096) 
		except usb.core.USBError as e:
			raise ValueError("Couldn't Read From Device In Init: %s" % str(e))



def main(argc, argv):

	#check for root permission (script can only be run as root)
	if getpass.getuser() != "root":
		print "Current user: " + getpass.getuser()
		print "Please run script as root user"
		sys.exit(0)

	#variables
	global socket_buffer

	#code to tell stmicro what to do
	send_data = b'\x04\x0c\x00\x00' #read one
	#send_data = b'\x04\x0d\x00\x00' #read all
	#send_data = b'\x04\x0e\x00\x00' #test case read

	vendor_id = 0x1268	#stmicro board
	product_id = 0xfffe	#stmicro board
	CFG_NUM = 0
	IFCE_NUM = 2
	EP_ADDR_WR = 3
	EP_ADDR_RD = 131	#0x83

	ST_config = CFG_NUM 		#User defined values to help look for correct 
	ST_interface = IFCE_NUM		#device information, overwritten with object
	ST_endpoint_wr = EP_ADDR_WR	#address if found
	ST_endpoint_rd = EP_ADDR_RD	#
	
	#Find usb device
	device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
	if device == None:
		raise ValueError("USB Device Not Found")
	else:
		print "Device found: Vendor ID =", "0x%0.4x" % vendor_id,", 0x%0.4x" % product_id
	
	#Get config, interface, endpoint
	try:
		for cfg in device:
			if cfg.iConfiguration == ST_config:
				ST_config = cfg
			for ifce in cfg:
				if ifce.bInterfaceNumber == ST_interface:
					ST_interface = ifce
				for ep in ifce:
					if ep.bEndpointAddress == ST_endpoint_wr:
						ST_endpoint_wr = ep
					if ep.bEndpointAddress == ST_endpoint_rd:
						ST_endpoint_rd = ep
		if (ST_config == CFG_NUM) or \
		   (ST_interface == IFCE_NUM) or \
		   (ST_endpoint_wr == EP_ADDR_WR) or \
		   (ST_endpoint_rd == EP_ADDR_RD):
			raise Exception
		print "Got config", ST_config.iConfiguration, \
		       ", interface", ST_interface.bInterfaceNumber, \
		       ", write endpoint", ST_endpoint_wr.bEndpointAddress, \
		       ", read endpoint", ST_endpoint_rd.bEndpointAddress
	
	except:
		print "Couldn't get device config, interface, endpoint"
		sys.exit(1)

	#check driver status
	if device.is_kernel_driver_active(ST_interface.bInterfaceNumber):
		try:
			device.detach_kernel_driver(ST_interface.bInterfaceNumber)
			print "Driver Detached"
		except usb.core.USBError as e:
			raise ValueError("Couldn't Detach Driver %s" % str(e))
	else:
		print "Driver Inactive"

	#Start server
	s = Server()
	s.start()
	
	#i = 0
	#while True:
	#	if i == 1000:
	#		temp_packet = [14, 0, 0, 0, 188, 127, 163, 14, 0, 10, 70, 104, 153, 1]
	#		process_raw(temp_packet)
	#		#print socket_buffer
	#		#socket_buffer = []
	#		i = 0
	#	else:
	#		i += 1

	#grab and toss out the first two readings
	usb_init(ST_endpoint_wr, ST_endpoint_rd)
	
	while True:
	#for i in range(0,1):

		#Signal STmicro for data
		try:
			ST_endpoint_wr.write(send_data)
		except usb.core.USBError as e:
			raise ValueError("Couldn't Write To Device: %s" % str(e))
	
		#Read data from STmicro
		try:
			#data = ST_endpoint_rd.read(204) #read 204 bytes (max number of samples)
			data = ST_endpoint_rd.read(4096) 
			print data
			process_raw(data)
			#print "Processed data"
			#break
		except usb.core.USBError as e:
			if str(e) == "[Errno 110] Operation timed out":
				print "Timed Out"
				continue
			elif str(e) == "[Errno 75] Overflow":
				print "Overflow"
				continue
				#raise
			else:
				raise ValueError("Couldn't Read From Device: %s" % str(e))

		#Break out of program on interrupt
		except KeyboardInterrupt:
			print "\nProgram Killed"
			sys.exit()


	#i = 0
	#while True:
	#	if i == 100000:
	#		temp_packet = [14, 0, 0, 0, 188, 127, 255, 191, 0, 10, 70, 153, 25, 1]
	#		process_raw(temp_packet)
	#	else:
	#		i += 1
	
	##Single Read
	#try:
	#	send_data = b'\x04\x0c\x00\x00'
	#	#device.write(ST_endpoint_wr.bEndpointAddress, send_data, ST_interface.bInterfaceNumber)
	#	ST_endpoint_wr.write(send_data)
	#except usb.core.USBError as e:
	#	raise ValueError("Couldn't Write To Device: %s" % str(e))
	#
	#try:
        #	#data = device.read(ST_endpoint_wr.bEndpointAddress, ST_endpoint.wMaxPacketSize, ST_interface.bInterfaceNumber)
	#	data = ST_endpoint_rd.read(ST_endpoint_rd.wMaxPacketSize)
        #	process_raw(data)
        #except usb.core.USBError as e:
        #	if str(e) == "[Errno 110] Operation timed out":
        #		print "Timed Out"
        #	else:
        #		raise ValueError("Couldn't Read From Device: %s" % str(e))


	
if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
