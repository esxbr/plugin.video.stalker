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

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') ) 

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])


#xbmcgui.Dialog().ok(addonname, 'aaa')

xbmcplugin.setContent(addon_handle, 'movies')


mode = args.get('mode', None)

portal_name_1 = args.get('portal_url_1', None)
portal_url_1 = args.get('portal_url_1', None)
portal_mac_1 = args.get('portal_mac_1', None)

portal_name_2 = args.get('portal_url_1', None)
portal_url_2 = args.get('portal_url_1', None)
portal_mac_2 = args.get('portal_mac_2', None)

portal_name_3 = args.get('portal_url_3', None)
portal_url_3 = args.get('portal_url_3', None)
portal_mac_3 = args.get('portal_mac_3', None)

def configMac(number):
	custom_mac = xbmcplugin.getSetting(int(sys.argv[1]), 'custom_mac_' + number);
	portal_mac = xbmcplugin.getSetting(int(sys.argv[1]), 'portal_mac_' + number);
	
	if custom_mac != 'true':
		portal_mac = '';
		
	elif not (custom_mac == 'true' and re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", portal_mac.lower()) != None):
		xbmcgui.Dialog().notification(addonname, 'Custom Mac ' + number + ' is Invalid.', xbmcgui.NOTIFICATION_ERROR );
		portal_mac = '';
		
	return portal_mac;


if portal_url_1 is None:

	portal_name_1 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_1");
	parental = xbmcplugin.getSetting(int(sys.argv[1]), "parental");
	password = xbmcplugin.getSetting(int(sys.argv[1]), "password");
	
	portal_url_1 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_1");
	portal_mac_1 = configMac('1');
		
	portal_name_2 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_2");
	portal_url_2 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_2");
	portal_mac_2 = configMac('2');
	
	portal_name_3 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_3");
	portal_url_3 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_3");
	portal_mac_3 = configMac('3');
	
else:
	parental = parental[0];
	password = password[0];
	portal_name_1 = portal_name_1[0];
	portal_url_1 = portal_url_1[0];
	portal_mac_1 = portal_mac_1[0];
	
	portal_name_2 = portal_name_2[0];
	portal_url_2 = portal_url_2[0];
	portal_mac_2 = portal_mac_2[0];
	
	portal_name_3 = portal_name_3[0];
	portal_url_3 = portal_url_3[0];
	portal_mac_3 = portal_mac_3[0];
	


def addPortal(portal_name, portal_url, portal_mac ):
	if portal_url != '':
		url = build_url({
			'mode': 'genres', 
			'stalker_url' : portal_url, 
			'portal_mac' : portal_mac, 
			'title' : portal_name
			});
			
		cmd = 'XBMC.RunPlugin(' + base_url + '?mode=cache&stalker_url=' + portal_url + ')';		
		li = xbmcgui.ListItem(portal_name, iconImage='DefaultProgram.png')
		li.addContextMenuItems([ ('Clear Cache', cmd) ]);

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
def build_url(query):
	return base_url + '?' + urllib.urlencode(query)


def homeLevel():

	addPortal(portal_name_1,portal_url_1, portal_mac_1);
	addPortal(portal_name_2,portal_url_2, portal_mac_2);
	addPortal(portal_name_3,portal_url_3, portal_mac_3);
	xbmcplugin.endOfDirectory(addon_handle);

def genreLevel():
	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];
	
	portal_mac = args.get('portal_mac', '');
	if portal_mac != '':
		portal_mac = portal_mac[0];
	
	try:
		data = load_channels.getGenres(portal_mac, stalker_url, addondir);
		
	except:
		xbmcgui.Dialog().notification(addonname, 'Server Offline', xbmcgui.NOTIFICATION_ERROR );
		return;
	
	
	
	data = data['genres'];
	

		
	url = build_url({
		'mode': 'vod', 
		'stalker_url' : stalker_url, 
		'portal_mac' : portal_mac
	});
			
	li = xbmcgui.ListItem('VoD', iconImage='DefaultVideo.png')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
	for i in data:

		id 		= i["id"];
		title 	= i["title"];
		
		#xbmcgui.Dialog().ok(addonname, title);
		
		url = build_url({
			'mode': 'channels', 
			'stalker_url' : stalker_url, 
			'genre_id': id, 
			'genre_name': title.title(), 
			'portal_mac' : portal_mac
			});
			
		if id == '10':
			iconImage = 'OverlayLocked.png';
		else:
			iconImage = 'DefaultVideo.png';
			
		li = xbmcgui.ListItem(title.title(), iconImage=iconImage)
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
		

	xbmcplugin.endOfDirectory(addon_handle);

def vodLevel():
	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];
	
	portal_mac = args.get('portal_mac', '');
	if portal_mac != '':
		portal_mac = portal_mac[0];
	
	try:
		data = load_channels.getVoD(portal_mac, stalker_url, addondir);
		
	except:
		xbmcgui.Dialog().notification(addonname, 'Server Offline', xbmcgui.NOTIFICATION_ERROR );
		return;
	
	
	data = data['vod'];
	
		
	for i in data:
		name 	= i["name"];
		cmd 	= i["cmd"];
		logo 	= i["logo"];
		
		
		if logo != '':
			logo_url = stalker_url + logo;
		else:
			logo_url = 'DefaultVideo.png';
				
				
		url = build_url({
				'mode': 'play', 
				'stalker_url' : stalker_url, 
				'cmd': cmd, 
				'tmp' : '0', 
				'title' : name.encode("utf-8"),
				'genre_name' : 'VoD',
				'logo_url' : logo_url, 
				'portal_mac' : portal_mac
				});
			

		li = xbmcgui.ListItem(name, iconImage=logo_url, thumbnailImage=logo_url)
		li.setInfo(type='Video', infoLabels={ "Title": name })
		#li.setProperty('IsPlayable', 'true')

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
	
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED);
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE);
	xbmcplugin.endOfDirectory(addon_handle);

def channelLevel():
	stop=False;
	
	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];
	
	genre_id_main = args.get('genre_id', None);
	genre_id_main = genre_id_main[0];
	
	portal_mac = args.get('portal_mac', '');
	if portal_mac != '':
		portal_mac = portal_mac[0];
	
	try:
		data = load_channels.getAllChannels(portal_mac, stalker_url, addondir);
		
	except:
		xbmcgui.Dialog().notification(addonname, 'Server Offline', xbmcgui.NOTIFICATION_ERROR );
		return;
	
	
	data = data['channels'];
	
	genre_name 	= args.get('genre_name', None);
	
	
	if genre_id_main == '10' and parental == 'true':
		result = xbmcgui.Dialog().input('Parental', hashlib.md5(password.encode('utf-8')).hexdigest(), type=xbmcgui.INPUT_PASSWORD, option=xbmcgui.PASSWORD_VERIFY);
		if result == '':
			stop = True;

	if stop == False:
		for i in data:
			name 	= i["name"];
			cmd 	= i["cmd"];
			tmp 	= i["tmp"];
			number 	= i["number"];
			genre_id 	= i["genre_id"];
			logo 	= i["logo"];
		
			if genre_id_main == '*' and genre_id == '10' and parental == 'true':
				continue;
		
			if genre_id_main == genre_id or genre_id_main == '*':
		
				if logo != '':
					logo_url = stalker_url + '/stalker_portal/misc/logos/320/' + logo;
				else:
					logo_url = 'DefaultVideo.png';
				
				
				url = build_url({
					'mode': 'play', 
					'stalker_url' : stalker_url, 
					'cmd': cmd, 
					'tmp' : tmp, 
					'title' : name.encode("utf-8"),
					'genre_name' : genre_name,
					'logo_url' : logo_url, 
					'portal_mac' : portal_mac
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

	stalker_url = args.get('stalker_url', None)
	stalker_url = stalker_url[0];
	
	portal_mac = args.get('portal_mac', '');
	if portal_mac != '':
		portal_mac = portal_mac[0];
	
	title 	= args['title'][0];
	cmd 	= args['cmd'][0];
	tmp 	= args['tmp'][0];
	genre_name 	= args['genre_name'][0];
	logo_url 	= args['logo_url'][0];
	
	try:
		if genre_name!='VoD':
			url = load_channels.retriveUrl(portal_mac, stalker_url, cmd, tmp);
		else:
			url = load_channels.retriveVoD(portal_mac, stalker_url, cmd);
	
	except:
		dp.close();
		
		xbmcgui.Dialog().notification(addonname, 'Channel Offline', xbmcgui.NOTIFICATION_INFO );
		return;
	
	dp.update(80);
	
	li = xbmcgui.ListItem(title, iconImage=logo_url);
	li.setInfo('video', {'Title': title, 'Genre': genre_name});
	xbmc.Player().play(item=url, listitem=li);
	
	dp.update(100);
	
	dp.close();

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





	