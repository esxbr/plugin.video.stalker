import sys
import urllib
import urllib2
import json
import os
import urlparse
import re, uuid
from time import time
from datetime import datetime
import math

key = ''
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def setMac(nmac):
	global mac;
	
	if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", nmac.lower()):
		mac = nmac;

def getMac():
	global mac;
	return mac;

def handshake(url):
	global key;
	
	info = retrieveData(url, values = {
		'type' : 'stb', 
		'action' : 'handshake',
		'JsHttpRequest' : '1-xml'})

	key = info['js']['token']
	
	#getProfile(url);
	
	#print 'key: ' + key

def getProfile(url):
	global mac, key;
		
	sn = "".join(re.findall("[0-9]+", mac));
	sn += sn + sn;
	sn = sn[:13];

	info = retrieveData(url, values = {
		'type' : 'stb', 
		'action' : 'get_profile',
		'hd' : '1',
		'ver' : 'ImageDescription:%200.2.18-r10-pub-250;%20ImageDate:%2014%20Jan%202015%2013:18:32%20GMT%200200;%20PORTAL%20version:%20Latest;%20API%20Version:%20JS%20API%20version:%20328;%20STB%20API%20version:%20134;%20Player%20Engine%20version:%200x560',
		'num_banks' : '1',
		'sn' : sn,
		'stb_type' : 'MAG250',
		'image_version' : '218',
		'auth_second_step' : '0',
		'hw_version' : '1.7-BD-00',
		'not_valid_token' : '0',
		'JsHttpRequest' : '1-xml'})


def retrieveData(url, values ):
	global key, mac;
	
	
	url += '/stalker_portal'
	load = '/server/load.php'
	refer = '/c/'
	timezone = 'Europe%2FKiev';

	user_agent 	= 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3';
	
	if key != '':
		#print 'Authorization Bearer ' + key;
		
		headers 	= { 
			'User-Agent' : user_agent, 
			'Cookie' : 'mac=' + mac.replace(':', '%3') + '; stb_lang=en; timezone=' + timezone,
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


def getGenres(portal_mac, url, path):	
	global key;
	now = time();
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl + '-genres';
	
	setMac(portal_mac);
	
	if not os.path.exists(path): 
		os.makedirs(path);
	
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
	
def getVoD(portal_mac, url, path):	
	global key;
	now = time();
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl + '-vod';
	
	setMac(portal_mac);
	
	if not os.path.exists(path):
		os.makedirs(path)
	
	if os.path.exists(portalurl):
		#check last time
		with open(portalurl) as data_file: data = json.load(data_file);
	
		time_init = float(data['time']);
		
	
		# update 12h
		if ((now - time_init) / 3600) < 12:
			return data;
	
	handshake(url);
	
	data = '{ "time" : "' + str(now) + '", "vod" : [ \n'
	
	page = 1;
	pages = 0;
	total_items = 1.0;
	max_page_items = 1.0;
	
	while True:
		info = retrieveData(url, values = {
			'type' : 'vod', 
			'action' : 'get_ordered_list',
			'sortby' : 'added',
			'not_ended' : '0',
			'p' : page,
			'fav' : '0',
			'JsHttpRequest' : '1-xml'})
		
		total_items = float(info['js']['total_items']);
		max_page_items = float(info['js']['max_page_items']);
		pages = math.ceil(total_items/max_page_items);
		
		results = info['js']['data']


		for i in results:
			name 	= i["name"]
			cmd 	= i['cmd']
			logo 	= i["screenshot_uri"]
		
			data += '{"name":"'+ name +'", "cmd":"'+ cmd +'", "logo":"'+ logo +'"}, \n'

		page += 1;
		if page > pages or page == 10:
			break;

	data = data[:-3] + '\n]}'

	with open(portalurl, 'w') as f: f.write(data.encode('utf-8'));
	
	return json.loads(data.encode('utf-8'));

def getAllChannels(portal_mac, url, path):

	now = time();
	
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	portalurl = path + '/' + portalurl
	
	setMac(portal_mac);
	
	if not os.path.exists(path):
		os.makedirs(path)

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


	page = 1;
	pages = 0;
	total_items = 1.0;
	max_page_items = 1.0;

	while True:
		# retrieve adults
		info = retrieveData(url, values = {
			'type' : 'itv', 
			'action' : 'get_ordered_list',
			'genre' : '10',
			'p' : page,
			'fav' : '0',
			'JsHttpRequest' : '1-xml'})
	
		total_items = float(info['js']['total_items']);
		max_page_items = float(info['js']['max_page_items']);
		pages = math.ceil(total_items/max_page_items);
	
		results = info['js']['data']

		for i in results:
			number 	= i["number"]
			name 	= i["name"]
			cmd 	= i['cmd']
			logo 	= i["logo"]
			tmp 	= i["use_http_tmp_link"]
			genre_id 	= i["tv_genre_id"];
		
			data += '{"number":"'+ number +'", "name":"'+ name +'", "cmd":"'+ cmd +'", "logo":"'+ logo +'", "tmp":"'+ str(tmp) +'", "genre_id":"'+ str(genre_id) +'"}, \n'

		page += 1;
		if page > pages:
			break;
	
	data = data[:-3] + '\n]}'
	

	with open(portalurl, 'w') as f: f.write(data.encode('utf-8'));
	
	return json.loads(data.encode('utf-8'));

def retriveUrl(portal_mac, url, channel, tmp):
	
	cmd = channel;
	
	setMac(portal_mac);
	
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


def retriveVoD(portal_mac, url, video):
	
	setMac(portal_mac);
		
	s = video.split(' ');
	url = s[0];
	if len(s)>1:
		url = s[1];

	
	url = url.replace('TOMTOM:', 'http://');
	
	#print url;

	# RETRIEVE THE 1 EXTM3U
	request = urllib2.Request(url)
	response  = urllib2.urlopen(request);
	url = response.geturl();


	# RETRIEVE THE 1 EXTM3U
	request = urllib2.Request(url)
	#request.get_method = lambda : 'HEAD'
	response  = urllib2.urlopen(request);
	data = response.read().decode("utf-8");
	data = data.splitlines();
	data = data[len(data) - 1];
	
	# RETRIEVE THE 2 EXTM3U
	url = response.geturl().split('?')[0];
	url_base = url[: -(len(url) - url.rfind('/'))]
	return url_base + '/' + data;

def clearCache(url, path):
	
	portalurl = "_".join(re.findall("[a-zA-Z0-9]+", url));
	
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.startswith(portalurl):
				os.remove(root + '/' + file);
	

def main(argv):

      if argv[0] == 'load':
      	getAllChannels('', argv[1], argv[2]);
      	
      elif argv[0] == 'genres':
      	getGenres('', argv[1], argv[2]);
      	
      elif argv[0] == 'vod':
      	getVoD('', argv[1], argv[2]);
      	
      elif argv[0] == 'channel':
      	url = retriveUrl('', argv[1], argv[2], argv[3]);
      	print url
	
      elif argv[0] == 'vod_url':
      	url = retriveVoD('', argv[1], argv[2]);
      	print url
      	os.system('/Applications/VLC.app/Contents/MacOS/VLC ' + url)
      	
      elif argv[0] == 'cache':
      	clearCache(argv[1], argv[2]);
      	
      elif argv[0] == 'profile':
      	handshake(argv[1]);



if __name__ == "__main__":
   main(sys.argv[1:])


