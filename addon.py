import sys
import os
import json
import urllib
import urlparse
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

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
go = True;

#xbmcgui.Dialog().ok(addonname, 'aaa')

xbmcplugin.setContent(addon_handle, 'movies')


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


def addPortal(portal):


	url = build_url({
		'mode': 'genres', 
		'portal' : json.dumps(portal)
		});
	
	cmd = 'XBMC.RunPlugin(' + base_url + '?mode=cache&stalker_url=' + portal['url'] + ')';	
	
	li = xbmcgui.ListItem(portal['name'], iconImage='DefaultProgram.png')
	li.addContextMenuItems([ ('Clear Cache', cmd) ]);

	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
def build_url(query):
	return base_url + '?' + urllib.urlencode(query)


def homeLevel():
	global portal_1, portal_2, portal_3, go;
	
	#todo - check none portal

	if go:
		addPortal(portal_1);
		addPortal(portal_2);
		addPortal(portal_3);
	
		xbmcplugin.endOfDirectory(addon_handle);

def genreLevel():
	
	try:
		data = load_channels.getGenres(portal['mac'], portal['url'], portal['serial'], addondir);
		
	except Exception as e:
		error = 'Server Offline';
		if 'Authorization failed' in str(e):
			error = 'Authorization failed.';
		xbmcgui.Dialog().notification(addonname, error, xbmcgui.NOTIFICATION_ERROR );
		
		return;

	data = data['genres'];
		
	url = build_url({
		'mode': 'vod', 
		'portal' : json.dumps(portal)
	});
			
	li = xbmcgui.ListItem('VoD', iconImage='DefaultVideo.png')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
	for i in data:

		id 		= i["id"];
		title 	= i["title"];
		
		#xbmcgui.Dialog().ok(addonname, title);
		
		url = build_url({
			'mode': 'channels', 
			'genre_id': id, 
			'genre_name': title.title(), 
			'portal' : json.dumps(portal)
			});
			
		if id == '10':
			iconImage = 'OverlayLocked.png';
		else:
			iconImage = 'DefaultVideo.png';
			
		li = xbmcgui.ListItem(title.title(), iconImage=iconImage)
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
		

	xbmcplugin.endOfDirectory(addon_handle);

def vodLevel():
	
	try:
		data = load_channels.getVoD(portal['mac'], portal['url'], portal['serial'], addondir);
		
	except:
		error = 'Server Offline';
		if 'Authorization failed' in str(e):
			error = 'Authorization failed.';
		xbmcgui.Dialog().notification(addonname, error, xbmcgui.NOTIFICATION_ERROR );
		return;
	
	
	data = data['vod'];
	
		
	for i in data:
		name 	= i["name"];
		cmd 	= i["cmd"];
		logo 	= i["logo"];
		
		
		if logo != '':
			logo_url = portal['url'] + logo;
		else:
			logo_url = 'DefaultVideo.png';
				
				
		url = build_url({
				'mode': 'play', 
				'cmd': cmd, 
				'tmp' : '0', 
				'title' : name.encode("utf-8"),
				'genre_name' : 'VoD',
				'logo_url' : logo_url, 
				'portal' : json.dumps(portal)
				});
			

		li = xbmcgui.ListItem(name, iconImage=logo_url, thumbnailImage=logo_url)
		li.setInfo(type='Video', infoLabels={ "Title": name })

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
	
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED);
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE);
	xbmcplugin.endOfDirectory(addon_handle);

def channelLevel():
	stop=False;
		
	try:
		data = load_channels.getAllChannels(portal['mac'], portal['url'], portal['serial'], addondir);
		
	except:
		error = 'Server Offline';
		if 'Authorization failed' in str(e):
			error = 'Authorization failed.';
		xbmcgui.Dialog().notification(addonname, error, xbmcgui.NOTIFICATION_ERROR );
		return;
	
	
	data = data['channels'];
	genre_name 	= args.get('genre_name', None);
	
	genre_id_main = args.get('genre_id', None);
	genre_id_main = genre_id_main[0];
	
	if genre_id_main == '10' and portal['parental'] == 'true':
		result = xbmcgui.Dialog().input('Parental', hashlib.md5(portal['password'].encode('utf-8')).hexdigest(), type=xbmcgui.INPUT_PASSWORD, option=xbmcgui.PASSWORD_VERIFY);
		if result == '':
			stop = True;

	
	if stop == False:
		for i in data:
			name 		= i["name"];
			cmd 		= i["cmd"];
			tmp 		= i["tmp"];
			number 		= i["number"];
			genre_id 	= i["genre_id"];
			logo 		= i["logo"];
		
			if genre_id_main == '*' and genre_id == '10' and portal['parental'] == 'true':
				continue;
		
		
			if genre_id_main == genre_id or genre_id_main == '*':
		
				if logo != '':
					logo_url = portal['url'] + '/stalker_portal/misc/logos/320/' + logo;
				else:
					logo_url = 'DefaultVideo.png';
				
				
				url = build_url({
					'mode': 'play', 
					'cmd': cmd, 
					'tmp' : tmp, 
					'title' : name.encode("utf-8"),
					'genre_name' : genre_name,
					'logo_url' : logo_url,  
					'portal' : json.dumps(portal)
					});
			

				li = xbmcgui.ListItem(name, iconImage=logo_url, thumbnailImage=logo_url);
				li.setInfo(type='Video', infoLabels={ 
					'title': name,
					'count' : number
					});

				xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li);
		
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER);
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE);
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_PROGRAM_COUNT);
		
		
		xbmcplugin.endOfDirectory(addon_handle);

def playLevel():
	
	dp = xbmcgui.DialogProgressBG();
	dp.create('IPTV', 'Loading ...');
	
	title 	= args['title'][0];
	cmd 	= args['cmd'][0];
	tmp 	= args['tmp'][0];
	genre_name 	= args['genre_name'][0];
	logo_url 	= args['logo_url'][0];
	
	
	try:
		if genre_name != 'VoD':
			url = load_channels.retriveUrl(portal['mac'], portal['url'], portal['serial'], cmd, tmp);
		else:
			url = load_channels.retriveVoD(portal['mac'], portal['url'], portal['serial'], cmd);

	
	except:
		dp.close();
		
		error = 'Channel Offline';
		if 'Authorization failed' in str(e):
			error = 'Authorization failed.';
		xbmcgui.Dialog().notification(addonname, error, xbmcgui.NOTIFICATION_INFO );
		return;
	
	dp.update(80);
	
	
	
	title += ' (' + portal['name'] + ')';
	
	li = xbmcgui.ListItem(title, iconImage=logo_url);
	li.setInfo('video', {'Title': title, 'Genre': genre_name});
	xbmc.Player().play(item=url, listitem=li);
	
	dp.update(100);
	
	dp.close();


mode = args.get('mode', None);
portal =  args.get('portal', None)

if portal is None:
	portal_1 = portalConfig('1');
	portal_2 = portalConfig('2');
	portal_3 = portalConfig('3');	
else:
	portal = json.loads(portal[0]);


if mode is None:
	homeLevel();

elif mode[0] == 'cache':	
	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];	
	load_channels.clearCache(stalker_url, addondir);

elif mode[0] == 'genres':
	genreLevel();
		
elif mode[0] == 'vod':
	vodLevel();

elif mode[0] == 'channels':
	channelLevel();
	
elif mode[0] == 'play':
	playLevel();
	
elif mode[0] == 'server':
	server.startServer(_portals = { '1' : portal_1, '2' : portal_2, '3' : portal_3 });
	xbmcgui.Dialog().ok(addonname, json.dumps(portal_1));
	





	