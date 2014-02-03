#!/usr/bin/python
#
# Created by: Jacob Branaugh
# Created on: 02/02/2014 22:40
#
# Program to test use of USB with PyUSB
#

import sys
import usb.core


def main(argc, argv):
	#variables
	#vendor_id=0x046d	#wireless mouse dongle
	#product_id=0xc52b	#wireless mouse dongle
	vendor_id=0x046d	#wired mouse
	product_id=0xc06d	#wired mouse

	#Find usb device
	device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
	if device == None:
		raise ValueError("USB Device Not Found")
	else:
		print "Device found: Vendor ID =", "0x%0.4x" % vendor_id,", 0x%0.4x" % product_id

	#Get device endpoint
	endpoint = device[0][(0,0)][0]

	#check driver status
	#print device.is_kernel_driver_active(0)
	if device.is_kernel_driver_active(0):
		try:
			device.detach_kernel_driver(0)
			print "Driver Detached"
		except usb.core.USBError as e:
			raise ValueError("Couldn't Detach Driver %s" % str(e))
	else:
		print "Driver Inactive"

	#configure
	try:
		device.set_configuration()
	except usb.core.USBError as e:
		raise ValueError("Couldn't Configure Device %s" % str(e))
	#device.reset()
	
	while True:
		try:
			data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, 0)
			print data
		except usb.core.USBError as e:
			if str(e) == "[Errno 110] Operation timed out":
				print "Timed Out"
				continue
			else:
				raise ValueError("Couldn't Read From Device: %s" % str(e))
		except KeyboardInterrupt:
			print "\nProgram Killed"
			sys.exit()
		
if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
