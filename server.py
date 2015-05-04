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

_PORT = 8899;
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') ) 

portals = None;
server = None;

class MyTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global portals, server, _PORT;
        

        try:
            if 'channels.html' in self.path:
            
            	host = self.headers.get('Host');
            
            	args = parse_qs(urlparse(self.path).query)         	
            	numportal = args['portal'][0];
            	portal = portals[numportal];
            	
            	data = load_channels.getAllChannels(portal['mac'], portal['url'], portal['serial'], addondir);
                data = data['channels']
                

                EXTM3U = "#EXTM3U\n";
                
                for i in data:
					name 		= i["name"];
					cmd 		= i["cmd"];
					tmp 		= i["tmp"];
					number 		= i["number"];
					genre_id 	= i["genre_id"];
					logo 		= i["logo"];

					if logo != '':
						logo = portal['url'] + '/stalker_portal/misc/logos/320/' + logo;
				
					
					parameters = urllib.urlencode( { 'channel' : cmd, 'tmp' : tmp, 'portal' : numportal } );
					
					EXTM3U += '#EXTINF:-1, tvg-id="' + number + '" tvg-logo="' + logo + '" group-title="LIVE TV", ' + name + '\n';
					EXTM3U += 'http://' + host + '/live.html?'  + parameters +'\n\n';
        	
        	
                self.send_response(200)
                self.send_header('Content-type',	'application/x-mpegURL')
                self.send_header('Connection',	'close')
                self.send_header('Content-Length', len(EXTM3U))
                self.end_headers()
                self.wfile.write(EXTM3U.encode('utf-8'))
                self.finish()
               
               
            elif 'live.html' in self.path:
				
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


def startServer(_portals):
	global server, portals, _PORT;
	
	portals = _portals;
	
	try:
		server = MyTCPServer(('', _PORT), MyHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()



