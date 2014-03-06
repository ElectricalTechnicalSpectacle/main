#!/usr/bin/python
#
# Created by: Jacob Branaugh
# Created on: 12/18/2013 01:57
#
# Program 
#

import sys
import usb.core

def main(argc, argv):

	vendor_id = 0x1268	#stmicro board
	product_id = 0xfffe	#stmicro board

	dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

	for cfg in dev:
		for ifce in cfg:
			for ep in ifce:
				print ""
				print "device:", dev, " config:", cfg, " Interface:", ifce, " Endpoint:", ep
				print ""
				#print ep.bEndpointAddress
				#print out all of these data things from the pyusb source core.py file
	

if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
