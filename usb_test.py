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

#################################################################################
###################### SOCKET STUFF #############################################
#################################################################################
#PORT =      59481
#HOST =      '127.0.0.1'
#BACKLOG =   5
#BUFF =      2048
#
#class Server:
#    def __init__(self):
#        self.host = HOST
#        self.port = PORT
#        self.conn = (self.host, self.port)
#        self.backlog = BACKLOG
#        self.server = None
#        self.threads = []
#        self.clients = []
#
#    def register_signals(self):
#        signal.signal(signal.SIGHUP, self.signal_handler)
#        signal.signal(signal.SIGINT, self.signal_handler)
#        signal.signal(signal.SIGQUIT, self.signal_handler)
#
#    def open_socket(self):
#        try:
#            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#            self.server.bind(self.conn)
#            self.server.listen(self.backlog)
#            print "Started server: " + str(self.host) + " on port: " + str(self.port)
#            print "Listening for incoming connections..."
#        except socket.error as message:
#            if self.server:
#                self.server.close()
#            print >> sys.stderr, "Could not open socket: " + str(message)
#            sys.exit(1)
#        self.register_signals()
#
#    def signal_handler(self, signum, frame):
#        print "Caught signal: ", signum
#        print "Closing the socket and cleaning up the mess..."
#        self.server_shutdown()
#
#    def server_shutdown(self):
#        self.running = 0
#        for c in self.threads:
#            try:
#                c.join()
#            except RuntimeError:
#                pass
#        if self.server:
#            self.server.close()
#        sys.exit(1)
#
#    def run(self):
#        self.open_socket()
#        inputs = [self.server, sys.stdin]
#        self.running = 1
#        while self.running:
#            try:
#                iready, oready, eready = select.select(inputs, [], [])
#            except select.error, err:
#                self.running = 0
#                pass
#            for s in iready:
#                if s == self.server:
#                    try:
#                        c = Client(self, self.server.accept())
#                        c.start()
#                        self.threads.append(c)
#                    except socket.error, err:
#                        pass
#
#                elif s == sys.stdin:
#                    junk = sys.stdin.readline()
#                    self.running = 0 
#
#                else:
#                    self.running = 0
#
#        # close all threads
#        print 'Closing....'
#        for c in self.threads:
#            c.join()
#        self.server_shutdown()
#
#
#class Client(threading.Thread):
#    def __init__(self, server, (client, address)):
#        threading.Thread.__init__(self)
#        self.client = client
#        self.address = address
#        self.server = server
#
#    def run(self):
#    	print "Incoming connection from : " + str(self.address)
#        running = 1
#        while running:
#            data = self.client.recv(BUFF)
#            if data:
#                if data == 'Hello':
#                    self.client.send("Hello back")
#
#                elif data == 'Test':
#                    num_1 = str(random.randint(1, 99999))
#                    num_2 = str(random.randint(1, 10)).rjust(2, '0')
#                    unit = random.choice(['mW', 'W', 'KW', 'MW']);
#                    full =  "|".join([num_1, num_2, unit])
#                    self.client.send(full)
#
#                elif data == 'Done':
#                    self.server.server_shutdown()
#                    running = 0
#            else:
#                running = 0
#        
#        self.client.close()
#    
#    def __repr__(self):
#        return str(self.address)
##############################################################################
##############################################################################
##############################################################################

# Data key for wired mouse:
# 
# |       0       |    1     |    2     |    3     |       4       |      5     |
# | button clicks | movement | movement | movement | wheel scrolls | wheel tilt |
#
# Data key for power info from STmicro
#                                                               |            Repeat However Many              |
# |      1 Byte       |     1 Byte      |  1 Byte   |  1 Byte   |   2 Byte    |   2 Byte    |     1 Byte      |
# |   Packet Length   |   Packet Type   |   Sum 1   |   Sum 2   |   Current   |   Voltage   |   Power State   |
#
def process_raw(packet, wr_buf):
	#Local variables
	NACK = 1

	try:
		length = int(packet[0])
		num_readings = (length - 4) / 5
		pkt_type = int(packet[1])
		if pkt_type == NACK:
			#Handle nack appropriately 
			print "Packet was a NACK"
			return

		check_1 = int(packet[2])	#Checksums not needed, only here to keep the
		check_2 = int(packet[3])	#numbers in order

		for idx in range(1, num_readings+1):
			voltage = ((int(packet[(i*4)+1]) << 8) | int(packet[i*4]))
			current = ((int(packet[(i*4)+3]) << 8) | int(packet[(i*4)+2]))
			pwr_state = int(packet[(i*4)+4])
			#build the string

		#test print
		print ("Packet Length:    " + str(length) + "\n" +
		       "Packet Type:      " + str(pkt_type) + "\n" +
		       "Checksum 1:       " + str(check_1) + "\n" +
		       "Checksum 2:       " + str(check_2) + "\n" +
		       "Current Reading:  " + str(current) + "\n" +
		       "Voltage Reading:  " + str(voltage) + "\n" +
		       "DUT Power State:  " + str(pwr_state) + "\n")
	except:
		print "Error: Invalid Packet"


def main(argc, argv):

	#check for root permission (script can only be run as root)
	if getpass.getuser() != "root":
		print "Current user: " + getpass.getuser()
		print "Please run script as root user"
		sys.exit(0)

	#variables
	socket_buffer = []

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

	##Start server
	#s = Server()
	#s.run()
	
	#while True:
	for i in range(0,10):

		#Signal STmicro for data
		try:
			send_data = b'\x04\x0c\x00\x00'
			ST_endpoint_wr.write(send_data)
		except usb.core.USBError as e:
			raise ValueError("Couldn't Write To Device: %s" % str(e))
	
		#Read data from STmicro
		try:
			data = ST_endpoint_rd.read(204) #read 204 bytes (max number of samples)
			process_raw(data, socket_buffer)
		except usb.core.USBError as e:
			if str(e) == "[Errno 110] Operation timed out":
				print "Timed Out"
				continue
			else:
				raise ValueError("Couldn't Read From Device: %s" % str(e))

		#Break out of program on interrupt
		except KeyboardInterrupt:
			print "\nProgram Killed"
			sys.exit()
	
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
