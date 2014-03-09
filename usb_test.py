#!/usr/bin/python
#
# Created by: Jacob Branaugh
# Created on: 02/02/2014 22:40
#
# Program to test use of USB with PyUSB
#
# Data key for wired mouse:
# 
# |       0       |    1     |    2     |    3     |       4       |      5     |
# | button clicks | movement | movement | movement | wheel scrolls | wheel tilt |
#
# Data key for power info from STmicro
# |39         24|23          8|7               0|
# |   Voltage   |   Current   |   Power State   |
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
import binascii

################################################################################
##################### SOCKET STUFF #############################################
################################################################################
###PORT =      59481
###HOST =      '127.0.0.1'
###BACKLOG =   5
###BUFF =      2048
###
###class Server:
###    def __init__(self):
###        self.host = HOST
###        self.port = PORT
###        self.conn = (self.host, self.port)
###        self.backlog = BACKLOG
###        self.server = None
###        self.threads = []
###        self.clients = []
###
###    def register_signals(self):
###        signal.signal(signal.SIGHUP, self.signal_handler)
###        signal.signal(signal.SIGINT, self.signal_handler)
###        signal.signal(signal.SIGQUIT, self.signal_handler)
###
###    def open_socket(self):
###        try:
###            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###            self.server.bind(self.conn)
###            self.server.listen(self.backlog)
###            print "Started server: " + str(self.host) + " on port: " + str(self.port)
###            print "Listening for incoming connections..."
###        except socket.error as message:
###            if self.server:
###                self.server.close()
###            print >> sys.stderr, "Could not open socket: " + str(message)
###            sys.exit(1)
###        self.register_signals()
###
###    def signal_handler(self, signum, frame):
###        print "Caught signal: ", signum
###        print "Closing the socket and cleaning up the mess..."
###        self.server_shutdown()
###
###    def server_shutdown(self):
###        self.running = 0
###        for c in self.threads:
###            try:
###                c.join()
###            except RuntimeError:
###                pass
###        if self.server:
###            self.server.close()
###        sys.exit(1)
###
###    def run(self):
###        self.open_socket()
###        inputs = [self.server, sys.stdin]
###        self.running = 1
###        while self.running:
###            try:
###                iready, oready, eready = select.select(inputs, [], [])
###            except select.error, err:
###                self.running = 0
###                pass
###            for s in iready:
###                if s == self.server:
###                    try:
###                        c = Client(self, self.server.accept())
###                        c.start()
###                        self.threads.append(c)
###                    except socket.error, err:
###                        pass
###
###                elif s == sys.stdin:
###                    junk = sys.stdin.readline()
###                    self.running = 0 
###
###                else:
###                    self.running = 0
###
###        # close all threads
###        print 'Closing....'
###        for c in self.threads:
###            c.join()
###        self.server_shutdown()
###
###
###class Client(threading.Thread):
###    def __init__(self, server, (client, address)):
###        threading.Thread.__init__(self)
###        self.client = client
###        self.address = address
###        self.server = server
###
###    def run(self):
###    	print "Incoming connection from : " + str(self.address)
###        running = 1
###        while running:
###            data = self.client.recv(BUFF)
###            if data:
###                if data == 'Hello':
###                    self.client.send("Hello back")
###
###                elif data == 'Test':
###                    num_1 = str(random.randint(1, 99999))
###                    num_2 = str(random.randint(1, 10)).rjust(2, '0')
###                    unit = random.choice(['mW', 'W', 'KW', 'MW']);
###                    full =  "|".join([num_1, num_2, unit])
###                    self.client.send(full)
###
###                elif data == 'Done':
###                    self.server.server_shutdown()
###                    running = 0
###            else:
###                running = 0
###        
###        self.client.close()
###    
###    def __repr__(self):
###        return str(self.address)
################################################################################
################################################################################
################################################################################


def process_raw(arg):
	##clear strings
	#no_click = left_click = right_click = middle_click = back_click = forward_click = multi_click = False

	print arg

	#Click handling
#	if int(arg[0]) == 0:
#		click_string = "                  "
#	elif int(arg[0]) == 1:
#		click_string = "Left Click        "
#	elif int(arg[0]) == 2:
#		click_string = "Right Click       "
#	elif int(arg[0]) == 4:
#		click_string = "Middle Click      "
#	elif int(arg[0]) == 8:
#		click_string = "Back Click        "
#	elif int(arg[0]) == 16:
#		click_string = "Forward Click     "
#	else:
#		click_string = "Multiple Clicks   "
#
#	#Movement Handling
#	if (int(arg[1]) == 0) and (int(arg[2]) == 0) and (int(arg[3]) == 0):
#		move_string = "               "
#	else:
#		move_string = "Mouse Moving   "
#
#	#Scroll wheel handling
#	if int(arg[4]) == 0:
#		scroll_string = "              "
#	elif int(arg[4]) == 1:
#		scroll_string = "Scroll Up     "
#	elif int(arg[4]) == 255:
#		scroll_string = "Scroll Down   "
#
#	#Scroll wheel tilt
#	if int(arg[5]) == 0:
#		tilt_string = "               "
#	elif int(arg[5]) == 1:
#		tilt_string = "Tilted Right   "
#	elif int(arg[5]) == 255:
#		tilt_string = "Tilted Left    "
#
#	#Print formatted data
#	print click_string + move_string + scroll_string + tilt_string

def hex_to_str(num):
	tmp = str(hex(num))[2:]
	print tmp
	if (len(tmp) % 2) != 0:
		tmp = "0" + tmp
	return binascii.unhexlify(tmp)

def main(argc, argv):

	#check for root permission (script can only be run as root)
	if getpass.getuser() != "root":
		print "Current user: " + getpass.getuser()
		print "Please run script as root user"
		sys.exit(0)

	#variables
	#vendor_id=0x046d	#wired mouse
	#product_id=0xc06d	#wired mouse
	vendor_id = 0x1268	#stmicro board
	product_id = 0xfffe	#stmicro board

	ST_config = 0	 	#User defined values to help look for correct 
	ST_interface = 2	#device information, overwritten with object
	ST_endpoint_wr = 3 	#address if found
	ST_endpoint_rd = 131	#


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
		if ST_config == 0 or ST_interface == 2 or ST_endpoint_wr == 3 or ST_endpoint_rd == 131:
			raise Exception
		print "Got config", ST_config.iConfiguration, ", interface", ST_interface.bInterfaceNumber, ", write endpoint", ST_endpoint_wr.bEndpointAddress, ", read endpoint", ST_endpoint_rd.bEndpointAddress
	
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
###	#s = Server()
###	#s.run()
	#

	#Single Read
	try:
		send_data = b'\x04\x0c\x00\x00'
		#device.write(ST_endpoint_wr.bEndpointAddress, send_data, ST_interface.bInterfaceNumber)
		ST_endpoint_wr.write(send_data)
	except usb.core.USBError as e:
		raise ValueError("Couldn't Write To Device: %s" % str(e))
	
	try:
        	#data = device.read(ST_endpoint_wr.bEndpointAddress, ST_endpoint.wMaxPacketSize, ST_interface.bInterfaceNumber)
		data = ST_endpoint_rd.read(ST_endpoint_rd.wMaxPacketSize)
        	process_raw(data)
        except usb.core.USBError as e:
        	if str(e) == "[Errno 110] Operation timed out":
        		print "Timed Out"
        	else:
        		raise ValueError("Couldn't Read From Device: %s" % str(e))

	#while True:
	#	try:
	#		data = device.read(ST_endpoint.bEndpointAddress, ST_endpoint.wMaxPacketSize, ST_interface.bInterfaceNumber)
	#		process_raw(data)
	#	except usb.core.USBError as e:
	#		if str(e) == "[Errno 110] Operation timed out":
	#			print "Timed Out"
	#			continue
	#		else:
	#			raise ValueError("Couldn't Read From Device: %s" % str(e))
	#	except KeyboardInterrupt:
	#		print "\nProgram Killed"
	#		sys.exit()
		
if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
