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
import time

import server
import config

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') ) 

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
go = True;

#xbmcgui.Dialog().ok(addonname, 'aaa')

xbmcplugin.setContent(addon_handle, 'movies')




def addPortal(portal):

	if portal['url'] == '':
		return;

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
		xbmcgui.Dialog().notification(addonname, str(e), xbmcgui.NOTIFICATION_ERROR );
		
		return;

	data = data['genres'];
		
	url = build_url({
		'mode': 'vod', 
		'portal' : json.dumps(portal)
	});
			
	li = xbmcgui.ListItem('VoD', iconImage='DefaultVideo.png')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
	for id, i in data.iteritems():

		title 	= i["title"];
		
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
		
	except Exception as e:
		xbmcgui.Dialog().notification(addonname, str(e), xbmcgui.NOTIFICATION_ERROR );
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
		
	except Exception as e:
		xbmcgui.Dialog().notification(addonname, str(e), xbmcgui.NOTIFICATION_ERROR );
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
		for i in data.values():
			
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

	
	except Exception as e:
		dp.close();
		xbmcgui.Dialog().notification(addonname, str(e), xbmcgui.NOTIFICATION_ERROR );
		return;
	
	dp.update(80);
	
	title = title.decode("utf-8");
	
	title += ' (' + portal['name'] + ')';
	
	li = xbmcgui.ListItem(title, iconImage=logo_url);
	li.setInfo('video', {'Title': title, 'Genre': genre_name});
	xbmc.Player().play(item=url, listitem=li);
	
	dp.update(100);
	
	dp.close();


mode = args.get('mode', None);
portal =  args.get('portal', None)

if portal is None:
	portal_1 = config.portalConfig('1');
	portal_2 = config.portalConfig('2');
	portal_3 = config.portalConfig('3');	
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
	port = addon.getSetting('server_port');
	
	action =  args.get('action', None);
	action = action[0];
	
	dp = xbmcgui.DialogProgressBG();
	dp.create('IPTV', 'Working ...');
	
	if action == 'start':
	
		if server.serverOnline():
			xbmcgui.Dialog().notification(addonname, 'Server already started.\nPort: ' + str(port), xbmcgui.NOTIFICATION_INFO );
		else:
			server.startServer();
			time.sleep(5);
			if server.serverOnline():
				xbmcgui.Dialog().notification(addonname, 'Server started.\nPort: ' + str(port), xbmcgui.NOTIFICATION_INFO );
			else:
				xbmcgui.Dialog().notification(addonname, 'Server not started. Wait one moment and try again. ', xbmcgui.NOTIFICATION_ERROR );
				
	else:
		if server.serverOnline():
			server.stopServer();
			time.sleep(5);
			xbmcgui.Dialog().notification(addonname, 'Server stopped.', xbmcgui.NOTIFICATION_INFO );
		else:
			xbmcgui.Dialog().notification(addonname, 'Server is already stopped.', xbmcgui.NOTIFICATION_INFO );
			
	dp.close();





	