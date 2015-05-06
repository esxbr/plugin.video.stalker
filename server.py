import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import load_channels
import SocketServer
import socket
import SimpleHTTPServer
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import config


addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') ) 

portals = None;
server = None;


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global portals, server;
        

        try:
            if 'channels.m3u' in self.path or 'channels.html' in self.path:
            
            	host = self.headers.get('Host');
            
            	args = parse_qs(urlparse(self.path).query)         	
            	numportal = args['portal'][0];
            	portal = portals[numportal];
            	
            	data = load_channels.getAllChannels(portal['mac'], portal['url'], portal['serial'], addondir);
                data = load_channels.orderChannels(data['channels'].values());
                

                EXTM3U = "#EXTM3U\n";
                
                for i in data:
					name 		= i["name"];
					cmd 		= i["cmd"];
					tmp 		= i["tmp"];
					number 		= i["number"];
					genre_title = i["genre_title"];
					genre_id 	= i["genre_id"];
					logo 		= i["logo"];

					if logo != '':
						logo = portal['url'] + '/stalker_portal/misc/logos/320/' + logo;
				
					
					parameters = urllib.urlencode( { 'channel' : cmd, 'tmp' : tmp, 'portal' : numportal } );
					
					EXTM3U += '#EXTINF:-1, tvg-id="' + number + '" tvg-name="' + name + '" tvg-logo="' + logo + '" group-title="' + genre_title + '", ' + name + '\n';
					EXTM3U += 'http://' + host + '/live.m3u?'  + parameters +'\n\n';
        	
        	
                self.send_response(200)
                self.send_header('Content-type',	'application/x-mpegURL')
                self.send_header('Connection',	'close')
                self.send_header('Content-Length', len(EXTM3U))
                self.end_headers()
                self.wfile.write(EXTM3U.encode('utf-8'))
                self.finish()
               
               
            elif 'live.m3u' in self.path:
				
				args = parse_qs(urlparse(self.path).query);
				cmd = args['channel'][0];
				tmp = args['tmp'][0];
				numportal = args['portal'][0];
				
				portal = portals[numportal];
				
				url = load_channels.retriveUrl(portal['mac'], portal['url'], portal['serial'], cmd, tmp);
				
				self.send_response(301)
				self.send_header('Location', url)
				self.end_headers()
				self.finish()
                
            elif 'epg.xml' in self.path:
				
				args = parse_qs(urlparse(self.path).query);
				numportal = args['portal'][0];
				
				portal = portals[numportal];
				
				xml = load_channels.getEPG(portal['mac'], portal['url'], portal['serial'], addondir);
				
				self.send_response(200)
				self.send_header('Content-type',	'txt/xml')
				self.send_header('Connection',	'close')
				self.send_header('Content-Length', len(xml))
				self.end_headers()
				self.wfile.write(xml)
				self.finish()
                
                
            elif 'stop' in self.path:
				mgs = 'Done';
            	
				self.send_response(200)
				self.send_header('Content-type',	'text/html')
				self.send_header('Connection',	'close')
				self.send_header('Content-Length', len(mgs))
				self.end_headers()
				self.wfile.write(mgs.encode('utf-8'))
                
				server.socket.close();
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)



def startServer():
	global portals, server;
	
	server_enable = addon.getSetting('server_enable');
	port = int(addon.getSetting('server_port'));
	
	if server_enable != 'true':
		return;

	portals = { 
		'1' : config.portalConfig('1'), 
		'2' : config.portalConfig('2'), 
		'3' : config.portalConfig('3') };

	try:
		server = SocketServer.TCPServer(('', port), MyHandler);
		server.serve_forever();
		
	except KeyboardInterrupt:
		server.socket.close();


if __name__ == '__main__':
	startServer();
	

        

