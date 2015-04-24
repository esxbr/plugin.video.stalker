import sys
import urllib
import urllib2
import json
import os
import urlparse
import re, uuid
from time import time
from datetime import datetime

key=''

def handshake(url):
	global key;
	
	info = retrieveData(url, values = {
		'type' : 'stb', 
		'action' : 'handshake',
		'JsHttpRequest' : '1-xml'})

	key = info['js']['token']
	
	#print 'key: ' + key


def retrieveData(url, values ):
	global key;
	
	mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

	url += '/stalker_portal'
	load = '/server/load.php'
	refer = '/c/'
	timezone = 'Europe%2FKiev';

	user_agent 	= 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3';
	
	if key != '':
		#print 'Authorization Bearer ' + key;
		
		headers 	= { 
			'User-Agent' : user_agent, 
			'Cookie' : 'mac=' + mac+ '; stb_lang=en; timezone=' + timezone,
			'Referer' : url + refer,
			'Accept' : '*/*',
			'X-User-Agent' : 'Model: MAG250; Link: WiFi',
			'Authorization' : 'Bearer ' + key };
	
	else:
		headers 	= { 
			'User-Agent' : user_agent, 
			'Cookie' : 'mac=' + mac+ '; stb_lang=en; timezone=' + timezone,
			'Referer' : url + refer,
			'Accept' : '*/*',
			'X-User-Agent' : 'Model: MAG250; Link: WiFi' };
		


	data = urllib.urlencode(values);
	req = urllib2.Request(url + load, data, headers);
	data = urllib2.urlopen(req).read().decode("utf-8");
	info = json.loads(data)

	return info;


def getGenres(url, path):	
	global key;
	now = time();
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl + '-genres';
	
	
	if os.path.exists(portalurl):
		#check last time
		with open(portalurl) as data_file: data = json.load(data_file);
	
		time_init = float(data['time']);
		
	
		# update 12h
		if ((now - time_init) / 3600) < 12:
			return data;
	
	handshake(url);
	
	info = retrieveData(url, values = {
		'type' : 'itv', 
		'action' : 'get_genres',
		'JsHttpRequest' : '1-xml'})
		
	
	results = info['js']
	
	data = '{ "time" : "' + str(now) + '", "genres" : [ \n'

	for i in results:
		alias 	= i["alias"]
		id 		= i["id"]
		title 	= i['title']
		
		data += '{"id":"'+ id +'", "alias":"'+ alias +'", "title":"'+ title +'"}, \n'

	
	data = data[:-3] + '\n]}'

	with open(portalurl, 'w') as f: f.write(data.encode('utf-8'));
	
	return json.loads(data.encode('utf-8'));
	
def getVoD(url, path):	
	global key;
	now = time();
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl + '-vod';
	
	
	if os.path.exists(portalurl):
		#check last time
		with open(portalurl) as data_file: data = json.load(data_file);
	
		time_init = float(data['time']);
		
	
		# update 12h
		if ((now - time_init) / 3600) < 12:
			return data;
	
	handshake(url);
	
	info = retrieveData(url, values = {
		'type' : 'vod', 
		'action' : 'get_ordered_list',
		'JsHttpRequest' : '1-xml'})
		
	
	results = info['js']['data']
	
	
	data = '{ "time" : "' + str(now) + '", "vod" : [ \n'

	for i in results:
		name 	= i["name"]
		cmd 	= i['cmd']
		logo 	= i["screenshot_uri"]
		
		data += '{"name":"'+ name +'", "cmd":"'+ cmd +'", "logo":"'+ logo +'"}, \n'


	data = data[:-3] + '\n]}'

	with open(portalurl, 'w') as f: f.write(data.encode('utf-8'));
	
	return json.loads(data.encode('utf-8'));

def getAllChannels(url, path):

	now = time();
	
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl
	

	if os.path.exists(portalurl):
		#check last time
		with open(portalurl) as data_file: data = json.load(data_file);
	
		time_init = float(data['time']);
	
		# update 12h
		if ((now - time_init) / 3600) < 12:
			return data;
	
	handshake(url);
	
	info = retrieveData(url, values = {
		'type' : 'itv', 
		'action' : 'get_all_channels',
		'JsHttpRequest' : '1-xml'})
	
	results = info['js']['data']

	data = '{ "time" : "' + str(now) + '", "channels" : [ \n'

	for i in results:
		number 	= i["number"]
		name 	= i["name"]
		cmd 	= i['cmd']
		logo 	= i["logo"]
		tmp 	= i["use_http_tmp_link"]
		genre_id 	= i["tv_genre_id"];
		
		data += '{"number":"'+ number +'", "name":"'+ name +'", "cmd":"'+ cmd +'", "logo":"'+ logo +'", "tmp":"'+ str(tmp) +'", "genre_id":"'+ str(genre_id) +'"}, \n'

	
	data = data[:-3] + '\n]}'

	with open(portalurl, 'w') as f: f.write(data.encode('utf-8'));
	
	return json.loads(data.encode('utf-8'));

def retriveUrl(url, channel, tmp):
	
	cmd = channel;
	
	if tmp != "0":
		info = retrieveData(url, values = {
			'type' : 'itv', 
			'action' : 'create_link', 
			'cmd' : channel,
			'forced_storage' : 'undefined',
			'disable_ad' : '0',
			'JsHttpRequest' : '1-xml'});
		cmd = info['js']['cmd'];
		
	s = cmd.split(' ');
			
	url = s[0];
	
	if len(s)>1:
		url = s[1];
		
	#print url;

	if tmp != "0":
		# RETRIEVE THE 1 EXTM3U
		request = urllib2.Request(url)
		request.get_method = lambda : 'HEAD'
		response  = urllib2.urlopen(request);
		data = response.read().decode("utf-8");
		data = data.splitlines();
		data = data[len(data) - 1];
	
		# RETRIEVE THE 2 EXTM3U
		url = response.geturl().split('?')[0];
		url_base = url[: -(len(url) - url.rfind('/'))]
		return url_base + '/' + data;
	else:
		return url;



def main(argv):

      if argv[0] == 'load':
      	getAllChannels(argv[1], argv[2]);
      	
      elif argv[0] == 'genres':
      	getGenres(argv[1], argv[2]);
      	
      elif argv[0] == 'vod':
      	getVoD(argv[1], argv[2]);
      	
      elif argv[0] == 'channel':
      	url = retriveUrl(argv[1], argv[2], argv[3]);
      	print url
      	#os.system('/Applications/VLC.app/Contents/MacOS/VLC ' + url)

if __name__ == "__main__":
   main(sys.argv[1:])


