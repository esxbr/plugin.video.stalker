import sys
import os
import json
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin
import load_channels


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
portal_name_2 = args.get('portal_url_1', None)
portal_url_2 = args.get('portal_url_1', None)
portal_name_3 = args.get('portal_url_3', None)
portal_url_3 = args.get('portal_url_3', None)

#xbmcgui.Dialog().ok(addonname, 'aaa')

if portal_url_1 is None:
	portal_name_1 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_1")
	portal_url_1 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_1")
	portal_name_2 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_2")
	portal_url_2 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_2")
	portal_name_3 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_name_3")
	portal_url_3 = xbmcplugin.getSetting(int(sys.argv[1]), "portal_url_3")
else:
	portal_name_1 = portal_name_1[0];
	portal_url_1 = portal_url_1[0];
	portal_name_2 = portal_name_2[0];
	portal_url_2 = portal_url_2[0];
	portal_name_3 = portal_name_3[0];
	portal_url_3 = portal_url_3[0];
	


def addPortal(portal_name, portal_url):
	if portal_url != '':
		
		url = build_url({
			'mode': 'genres', 
			'stalker_url' : portal_url, 
			'title' : portal_name
			});
		
				
		li = xbmcgui.ListItem(portal_name, iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
	
	
def build_url(query):
	return base_url + '?' + urllib.urlencode(query)

if mode is None:

	addPortal(portal_name_1,portal_url_1);
	addPortal(portal_name_2,portal_url_2);
	addPortal(portal_name_3,portal_url_3);
		
		
elif mode[0] == 'genres':



	
	stalker_url = args.get('stalker_url', None)
	stalker_url = stalker_url[0];
	
	data = load_channels.getGenres(stalker_url, addondir);
	data = data['genres'];
	

		
	url = build_url({
		'mode': 'vod', 
		'stalker_url' : stalker_url
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
			'genre_name': title.title()
			});
		li = xbmcgui.ListItem(title.title(), iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True);
		
		
elif mode[0] == 'vod':


	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];
	
	
	data = load_channels.getVoD(stalker_url, addondir);
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
				'logo_url' : logo_url
				});
			

		li = xbmcgui.ListItem(name, iconImage=logo_url, thumbnailImage=logo_url)
		li.setInfo(type='Video', infoLabels={ "Title": name })
		#li.setProperty('IsPlayable', 'true')

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

	
elif mode[0] == 'channels':


	stalker_url = args.get('stalker_url', None);
	stalker_url = stalker_url[0];
	
	genre_id_main = args.get('genre_id', None);
	genre_id_main = genre_id_main[0];
	
	data = load_channels.getAllChannels(stalker_url, addondir);
	data = data['channels'];
	
	genre_name 	= args.get('genre_name', None);
	

	for i in data:
		name 	= i["name"];
		cmd 	= i["cmd"];
		tmp 	= i["tmp"];
		number 	= i["number"];
		genre_id 	= i["genre_id"];
		logo 	= i["logo"];
		
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
				'logo_url' : logo_url
				});
			

			li = xbmcgui.ListItem(name, iconImage=logo_url, thumbnailImage=logo_url)
			li.setInfo(type='Video', infoLabels={ "Title": name })
			#li.setProperty('IsPlayable', 'true')

			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

elif mode[0] == 'play':

	stalker_url = args.get('stalker_url', None)
	stalker_url = stalker_url[0];
	
	title 	= args['title'][0];
	cmd 	= args['cmd'][0];
	tmp 	= args['tmp'][0];
	genre_name 	= args['genre_name'][0];
	logo_url 	= args['logo_url'][0];
	
	if genre_name!='VoD':
		url = load_channels.retriveUrl(stalker_url, cmd, tmp);
	else:
		url = load_channels.retriveVoD(stalker_url, cmd);
	
	li = xbmcgui.ListItem(title, iconImage=logo_url);
	li.setInfo('video', {'Title': title, 'Genre': genre_name});
	xbmc.Player().play(item=url, listitem=li);



xbmcplugin.endOfDirectory(addon_handle)


	