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
	print "    bLength            =", dev.bLength
	print "    bDescriptorType    =", dev.bDescriptorType
	print "    bcdUSB             =", dev.bcdUSB             
	print "    bDeviceClass       =", dev.bDeviceClass       
	print "    bDeviceSubClass    =", dev.bDeviceSubClass    
	print "    bDeviceProtocol    =", dev.bDeviceProtocol    
	print "    bMaxPacketSize0    =", dev.bMaxPacketSize0    
	print "    idVendor           =", dev.idVendor           
	print "    idProduct          =", dev.idProduct          
	print "    bcdDevice          =", dev.bcdDevice          
	print "    iManufacturer      =", dev.iManufacturer      
	print "    iProduct           =", dev.iProduct           
	print "    iSerialNumber      =", dev.iSerialNumber      
	print "    bNumConfigurations =", dev.bNumConfigurations 
	print "    address            =", dev.address            
	print "    bus                =", dev.bus                
	print "    port_number        =", dev.port_number        
	print ""
	print ""
	print ""


	for cfg in dev:

		print "    Config:"
		print "        bLength             =", cfg.bLength
		print "        bDescriptorType     =", cfg.bDescriptorType
		print "        wTotalLength        =", cfg.wTotalLength
		print "        bNumInterfaces      =", cfg.bNumInterfaces
		print "        bConfigurationValue =", cfg.bConfigurationValue
		print "        iConfiguration      =", cfg.iConfiguration
		print "        bmAttributes        =", cfg.bmAttributes
		print "        bMaxPower           =", cfg.bMaxPower
		print "" 
		print "" 
		print "" 

		for ifce in cfg:

			print "        Interface:"
			print "            bLength            =", ifce.bLength
			print "            bDescriptorType    =", ifce.bDescriptorType
			print "            bInterfaceNumber   =", ifce.bInterfaceNumber
			print "            bAlternateSetting  =", ifce.bAlternateSetting
			print "            bNumEndpoints      =", ifce.bNumEndpoints
			print "            bInterfaceClass    =", ifce.bInterfaceClass
			print "            bInterfaceSubClass =", ifce.bInterfaceSubClass
			print "            bInterfaceProtocol =", ifce.bInterfaceProtocol
			print "            iInterface         =", ifce.iInterface
			print ""
			print ""
			print ""

			for ep in ifce:

				print "            Endpoint:"
				print "                bLength          =", ep.bLength
				print "                bDescriptorType  =", ep.bDescriptorType
				print "                bEndpointAddress =", ep.bEndpointAddress
				print "                bmAttributes     =", ep.bmAttributes
				print "                wMaxPacketSize   =", ep.wMaxPacketSize
				print "                bInterval        =", ep.bInterval
				print "                bRefresh         =", ep.bRefresh
				print "                bSynchAddress    =", ep.bSynchAddress
				print ""
				print ""
				print ""


if __name__ == "__main__":
	main(len(sys.argv), sys.argv) 
