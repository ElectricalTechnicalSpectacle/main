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

	print ""
	print ""
	print ""
	print "Device:"
	print "    bLength            =", "0x%0.4x" % dev.bLength
	print "    bDescriptorType    =", "0x%0.4x" % dev.bDescriptorType
	print "    bcdUSB             =", "0x%0.4x" % dev.bcdUSB             
	print "    bDeviceClass       =", "0x%0.4x" % dev.bDeviceClass       
	print "    bDeviceSubClass    =", "0x%0.4x" % dev.bDeviceSubClass    
	print "    bDeviceProtocol    =", "0x%0.4x" % dev.bDeviceProtocol    
	print "    bMaxPacketSize0    =", "0x%0.4x" % dev.bMaxPacketSize0    
	print "    idVendor           =", "0x%0.4x" % dev.idVendor           
	print "    idProduct          =", "0x%0.4x" % dev.idProduct          
	print "    bcdDevice          =", "0x%0.4x" % dev.bcdDevice          
	print "    iManufacturer      =", "0x%0.4x" % dev.iManufacturer      
	print "    iProduct           =", "0x%0.4x" % dev.iProduct           
	print "    iSerialNumber      =", "0x%0.4x" % dev.iSerialNumber      
	print "    bNumConfigurations =", "0x%0.4x" % dev.bNumConfigurations 
	print "    address            =", "0x%0.4x" % dev.address            
	print "    bus                =", "0x%0.4x" % dev.bus                
	print "    port_number        =", dev.port_number        
	print ""
	print ""
	print ""


	for cfg in dev:

		print "    Config:"
		print "        bLength             =", "0x%0.4x" % cfg.bLength
		print "        bDescriptorType     =", "0x%0.4x" % cfg.bDescriptorType
		print "        wTotalLength        =", "0x%0.4x" % cfg.wTotalLength
		print "        bNumInterfaces      =", "0x%0.4x" % cfg.bNumInterfaces
		print "        bConfigurationValue =", "0x%0.4x" % cfg.bConfigurationValue
		print "        iConfiguration      =", "0x%0.4x" % cfg.iConfiguration
		print "        bmAttributes        =", "0x%0.4x" % cfg.bmAttributes
		print "        bMaxPower           =", "0x%0.4x" % cfg.bMaxPower
		print "" 
		print "" 
		print "" 

		for ifce in cfg:

			print "        Interface:"
			print "            bLength            =", "0x%0.4x" % ifce.bLength
			print "            bDescriptorType    =", "0x%0.4x" % ifce.bDescriptorType
			print "            bInterfaceNumber   =", "0x%0.4x" % ifce.bInterfaceNumber
			print "            bAlternateSetting  =", "0x%0.4x" % ifce.bAlternateSetting
			print "            bNumEndpoints      =", "0x%0.4x" % ifce.bNumEndpoints
			print "            bInterfaceClass    =", "0x%0.4x" % ifce.bInterfaceClass
			print "            bInterfaceSubClass =", "0x%0.4x" % ifce.bInterfaceSubClass
			print "            bInterfaceProtocol =", "0x%0.4x" % ifce.bInterfaceProtocol
			print "            iInterface         =", "0x%0.4x" % ifce.iInterface
			print ""
			print ""
			print ""

			for ep in ifce:

				print "            Endpoint:"
				print "                bLength          =", "0x%0.4x" % ep.bLength
				print "                bDescriptorType  =", "0x%0.4x" % ep.bDescriptorType
				print "                bEndpointAddress =", "0x%0.4x" % ep.bEndpointAddress
				print "                bmAttributes     =", "0x%0.4x" % ep.bmAttributes
				print "                wMaxPacketSize   =", "0x%0.4x" % ep.wMaxPacketSize
				print "                bInterval        =", "0x%0.4x" % ep.bInterval
				print "                bRefresh         =", "0x%0.4x" % ep.bRefresh
				print "                bSynchAddress    =", "0x%0.4x" % ep.bSynchAddress
				print ""
				print ""
				print ""


if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
