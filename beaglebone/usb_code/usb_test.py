#!/usr/bin/python
#
# Created by: Jacob Branaugh
# Created on: 02/02/2014 22:40
#
# Program to test use of USB with PyUSB
#
# Data key for wired mouse:
# 
# |       0       |    1     |    2     |    3     |       4       | 5 |
# | button clicks | movement | movement | movement | wheel scrolls | ? |
#


import sys
import usb.core

def process_raw(arg):
	#clear flags
	no_click = left_click = right_click = middle_click = back_click = forward_click = multi_click = False

	print arg[0]

	#Click handling
	if int(arg[0]) == 0:
		click_string = "                  "
	elif int(arg[0]) == 1:
		click_string = "Left Click        "
	elif int(arg[0]) == 2:
		click_string = "Right Click       "
	elif int(arg[0]) == 4:
		click_string = "Middle Click      "
	elif int(arg[0]) == 8:
		click_string = "Back Click        "
	elif int(arg[0]) == 16:
		click_string = "Forward Click     "
	else:
		click_string = "Multiple Clicks   "

	#Scroll wheel handling
	if int(arg[4]) == 0:
		scroll_string = "              "
	elif int(arg[4]) == 1:
		scroll_string = "Scroll Down   "
	elif int(arg[4]) == 255:
		scroll_string = "Scroll Up     "

	#Movement Handling
	if (int(arg[1]) == 0) && (int(arg[2]) == 0) && (int(arg[3]) == 0):
		move_string = "               "
	else:
		move_string = "Mouse Moving   "


def main(argc, argv):
	#variables
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
			process_raw(data)
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
