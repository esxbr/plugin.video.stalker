import sys
import os
import json
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import load_channels
import hashlib
import re

import server

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') ) 


def portalConfig(number):

	portal = {};
	
	portal['parental'] = addon.getSetting("parental");
	portal['password'] = addon.getSetting("password");
	
	portal['name'] = addon.getSetting("portal_name_" + number);
	portal['url'] = addon.getSetting("portal_url_" + number);
	portal['mac'] = configMac(number);
	portal['serial'] = configSerialNumber(number);
		
	return portal;


def configMac(number):
	global go;
	
	custom_mac = addon.getSetting('custom_mac_' + number);
	portal_mac = addon.getSetting('portal_mac_' + number);
	
	if custom_mac != 'true':
		portal_mac = '';
		
	elif not (custom_mac == 'true' and re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", portal_mac.lower()) != None):
		xbmcgui.Dialog().notification(addonname, 'Custom Mac ' + number + ' is Invalid.', xbmcgui.NOTIFICATION_ERROR );
		portal_mac = '';
		go=False;
		
	return portal_mac;
	
	
def configSerialNumber(number):
	global go;
	
	send_serial = addon.getSetting('send_serial_' + number);
	custom_serial = addon.getSetting('custom_serial_' + number);
	serial_number = addon.getSetting('serial_number_' + number);
	device_id = addon.getSetting('device_id_' + number);
	device_id2 = addon.getSetting('device_id2_' + number);
	signature = addon.getSetting('signature_' + number);

	
	if send_serial != 'true':
		return None;
	
	elif send_serial == 'true' and custom_serial == 'false':
		return {'custom' : False};
		
	elif send_serial == 'true' and custom_serial == 'true':
	
		if serial_number == '' or device_id == '' or device_id2 == '' or signature == '':
			xbmcgui.Dialog().notification(addonname, 'Serial information is invalid.', xbmcgui.NOTIFICATION_ERROR );
			go=False;
			return None;
	
		return {'custom' : True, 'sn' : serial_number, 'device_id' : device_id, 'device_id2' : device_id2, 'signature' : signature};
		
	return None;