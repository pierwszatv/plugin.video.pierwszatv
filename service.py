﻿# -*- coding: utf-8 -*-
import time
import xbmc
import xbmcgui
import xbmcaddon
import threading
import SocketServer
import re
import os, sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import httpCommon
import pLog
import pierwszaTV

log = pLog.pLog()

httpClient = httpCommon.common()
API = pierwszaTV.pierwszaTV()

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addondir    = xbmc.translatePath( addon.getAddonInfo('profile') )

class MyHandler(BaseHTTPRequestHandler):
	def do_HEAD(self):
		#xbmcgui.Dialog().notification("TV Service", "HEAD", xbmcgui.NOTIFICATION_ERROR );
		try:
			if 'channel' in self.path:
				args = parse_qs(urlparse(self.path).query)
				channel = args['channel'][0]
				service = args['service'][0]
				channelUrl = API.getChannel(channel)
				self.send_response(301)
				log.error('STREAM_URL: ' + channelUrl)
				self.send_header('Location', channelUrl)
				self.end_headers()
				self.finish()
		except Exception as e:
			xbmcgui.Dialog().notification("TV Service", "HEAD Connection error, try again", xbmcgui.NOTIFICATION_ERROR );
	def do_GET(self):
		#host = self.headers.get('Host')
		try:
			if 'playlist' in self.path:
				playlist = API.getChannelsM3U()
				self.send_response(200)
				self.send_header('Content-type',    'application/x-mpegURL')
				self.send_header('Connection',    'close')
				self.send_header('Content-Length', len(playlist))
				self.end_headers()
				self.wfile.write(playlist.encode('utf-8'))
				self.finish()
			elif 'channel' in self.path:
				args = parse_qs(urlparse(self.path).query)
				channel = args['channel'][0]
				service = args['service'][0]
				channelUrl = API.getStreamUrl(channel)
				play_item = xbmcgui.ListItem(path=channelUrl)
				xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
				#self.send_response(301)
				#self.send_header('Location', '')
				#self.end_headers()
				#self.finish()
				return
			elif 'epg' in self.path:
				self.send_response(301)
				self.send_header('Location', 'http://epg.iptvlive.org')
				self.end_headers()
				self.finish()
			else:
				xbmcgui.Dialog().notification("TV Service", "Unsupported method called", xbmcgui.NOTIFICATION_ERROR );
		except Exception as e:
			log.error('TV Service: ' + str(e))
			xbmcgui.Dialog().notification("TV Service", "Connection error, try again", xbmcgui.NOTIFICATION_ERROR );

class AsyncCall(object):
	def __init__(self, fnc, callback = None):
		self.Callable = fnc
		self.Callback = callback
		
	def __call__(self, *args, **kwargs):
		self.Thread = threading.Thread(target = self.run, name = self.Callable.__name__, args = args, kwargs = kwargs)
		self.Thread.start()
		return self

	def wait(self, timeout = None):
		self.Thread.join(timeout)
		if self.Thread.isAlive():
			raise TimeoutError()
		else:
			return self.Result
			
	def run(self, *args, **kwargs):
		self.Result = self.Callable(*args, **kwargs)
		if self.Callback:
			self.Callback(self.Result)

class AsyncMethod(object):
	def __init__(self, fnc, callback=None):
		self.Callable = fnc
		self.Callback = callback
		
	def __call__(self, *args, **kwargs):
		return AsyncCall(self.Callable, self.Callback)(*args, **kwargs)
		
def Async(fnc = None, callback = None):
	if fnc == None:
		def AddAsyncCallback(fnc):
			return AsyncMethod(fnc, callback)
		return AddAsyncCallback
	else:
		return AsyncMethod(fnc, callback)
		
@Async
def startServer():
	global server;
	server_enable = addon.getSetting('server_enable');
	port = int(addon.getSetting('server_port'));
	#xbmcgui.Dialog().notification("Example", str(port), xbmcgui.NOTIFICATION_ERROR );
	if server_enable:
		try:
			server = SocketServer.TCPServer(('', port), MyHandler);
			server.serve_forever();
		except KeyboardInterrupt:
			if server != None:
				server.socket.close();

def serverOnline():
	port = addon.getSetting('server_port');
	try:
		url = urllib.urlopen('http://localhost:' + str(port) + '/online');
		code = url.getcode();
		if code == 200:
			return True;
	except Exception as e:
		return False;
	return False;


def stopServer():
	port = addon.getSetting('server_port');
	try:
		url = urllib.urlopen('http://localhost:' + str(port) + '/stop');
		code = url.getcode();
	except Exception as e:
		return;
	return;

if __name__ == '__main__':
	startServer();