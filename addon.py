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

stalker_url = args.get('stalker_url', None)

if stalker_url is None:
	stalker_url = xbmcplugin.getSetting(int(sys.argv[1]), "url")
else:
	stalker_url = stalker_url[0];
	
def build_url(query):
	return base_url + '?' + urllib.urlencode(query)

if mode is None:
	
	data = load_channels.getAllChannels(stalker_url, addondir);
	data = data['channels'];
	

	for i in data:
		name 	= i["name"];
		cmd 	= i["cmd"];
		tmp 	= i["tmp"];
		number 	= i["number"];
		
		url = build_url({'mode': 'folder', 'stalker_url' : stalker_url, 'cmd': cmd, 'tmp' : tmp, 'number' : number, 'title' : name.encode("utf-8")});
				
		li = xbmcgui.ListItem(name, iconImage='DefaultVideo.png')
		#li.setInfo(type='Video', infoLabels={ "Title": title })
		#li.setProperty('IsPlayable', 'true')

		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

elif mode[0] == 'folder':
	
	title 	= args['title'][0];
	number 	= args['number'][0];
	cmd 	= args['cmd'][0];
	tmp 	= args['tmp'][0];
	
	url = load_channels.retriveUrl(stalker_url, cmd, tmp);
	
	li = xbmcgui.ListItem(label=title, path=url)
	xbmc.Player().play(item=url, listitem=li)



xbmcplugin.endOfDirectory(addon_handle)


	