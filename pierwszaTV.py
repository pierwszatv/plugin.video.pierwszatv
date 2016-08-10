# -*- coding: utf-8 -*-
import os, sys
import playlist
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from datetime import datetime, timedelta
import httpCommon
import pLog
import json
import time
import threading

addon = xbmcaddon.Addon()
user = addon.getSetting('pierwsza_tv_user');
password = addon.getSetting('pierwsza_tv_pass');
api_id = "W4ER"
checksum = "a4d425e463160798c7aab988a67c1218"
API = "http://pierwsza.tv/api/"
AUTH_URL = "https://raw.githubusercontent.com/pierwszatv/repository.pierwszatv/master/auth.txt"

httpClient = httpCommon.common()
log = pLog.pLog()

class pierwszaTV:

	baseUrl = API.replace('/api', '')

	def __init__(self):
		self.urlStream = "a"
		pass
	def checkAuth(self):
		query_auth = {'url': AUTH_URL,'return_data': True, 'use_post': False}
		data_auth = httpClient.getURLRequestData(query_auth)
		if(data_auth != "\n"):
			xbmcgui.Dialog().notification("PierwszaTV", str(data_auth), xbmcgui.NOTIFICATION_ERROR )
			return False
		return True

	def getStreamUrl(self, channel):
		time.sleep(1)
		return self.urlStream
	def getChannel(self, channel):
		try:
			params_stream_create = 'api_id=' + api_id + '&checksum=' + checksum + '&id=' + channel + '&user=' + user + '&password=' + password
			query_stream_create = {'url': API + 'stream/create?' + params_stream_create,'return_data': True, 'use_post': False}
			data_stream_create = httpClient.getURLRequestData(query_stream_create)
			log.error('PierwszaTV: data_stream_create' + str(data_stream_create))
			jsonStreamCreate = json.loads(data_stream_create)
			streamCreateStatus = jsonStreamCreate['status']
			if streamCreateStatus == 'ok':
				tried = 0
				serverId = jsonStreamCreate['serverId']
				streamId = jsonStreamCreate['streamId']
				token = jsonStreamCreate['token']
				tokenExpireIn = jsonStreamCreate['tokenExpireIn']
				streamUrl = self.getChannelUrl(serverId, streamId, token, tried)
				self.urlStream = streamUrl
				expire = int(tokenExpireIn * 0.75)
				#time.sleep(5)
				threading.Thread(target=self.tokenRefresh, args=(streamId, serverId, token, expire,)).start()
				#threading.Thread(target=self.refreshToken, args=(streamId, serverId, token, tokenExpireIn,)).start()
				#tokenThread.setDaemon(True)
				#tokenThread.start()
				return streamUrl
			else:
				xbmcgui.Dialog().notification("PierwszaTV", "Error creating channel stream", xbmcgui.NOTIFICATION_ERROR )
		except Exception as e:
			log.error('PierwszaTV: ' + str(e))
			xbmcgui.Dialog().notification("PierwszaTV", str(e), xbmcgui.NOTIFICATION_ERROR )

	def getChannelUrl(self, serverId, streamId, token, tried):
		try:
			params_stream_status = 'api_id=' + api_id + '&checksum=' + checksum + '&serverId=' + str(serverId) + '&streamId=' + streamId
			query_stream_status = {'url': API + 'stream/status?' + params_stream_status,'return_data': True, 'use_post': False}
			data_stream_status = httpClient.getURLRequestData(query_stream_status)
			log.error('PierwszaTV: data_stream_status' + str(data_stream_status))
			jsonStreamStatus = json.loads(data_stream_status)
			streamStatusStatus = jsonStreamStatus['status']
			tried += 1
			#xbmcgui.Dialog().notification("PierwszaTV", "Tried: " + str(tried), xbmcgui.NOTIFICATION_ERROR )
			if streamStatusStatus == 'ok':
				started = jsonStreamStatus['started']
				sourceError = jsonStreamStatus['sourceError']
				if sourceError == True:
					xbmcgui.Dialog().notification("PierwszaTV", "Przerwa techniczna, spróbuj później", xbmcgui.NOTIFICATION_ERROR );
					return ''
				if started == False:
					time.sleep(5)
					return self.getChannelUrl(serverId, streamId, token, tried)
				else:
					source = jsonStreamStatus['source']
					streamURl = source + '?token=' + token
					#log.error('PierwszaTV Stream: ' + streamURl)
					return streamURl
			else:
				xbmcgui.Dialog().notification("PierwszaTV", "Status: Error", xbmcgui.NOTIFICATION_ERROR );
		except Exception as e:
			xbmcgui.Dialog().notification("PierwszaTV getChannelUrl:", str(e), xbmcgui.NOTIFICATION_ERROR );
	def getChannelsM3U(self):
		try:
			getChannelsReq = {'url': API + 'channels?api_id=' + api_id + '&checksum=' + checksum, 'return_data': True, 'use_post': False}
			getChannelsResp = httpClient.getURLRequestData(getChannelsReq)
			if getChannelsResp != None:
				return self.createPlaylist(getChannelsResp)
		except Exception as e:
			log.error('PierwszaTV: ' + str(e))
			xbmcgui.Dialog().notification("PierwszaTV", str(e), xbmcgui.NOTIFICATION_ERROR );
		#return "M3U_Content"
	def getChannels(self):
		#self.checkAuth()
		try:
			getChannelsReq = {'url': API + 'channels?api_id=' + api_id + '&checksum=' + checksum, 'return_data': True, 'use_post': False}
			getChannelsResp = httpClient.getURLRequestData(getChannelsReq)
			if getChannelsResp != None:
				return self.getChannelList(getChannelsResp)
		except Exception as e:
			log.error('PierwszaTV: ' + str(e))
			xbmcgui.Dialog().notification("PierwszaTV", str(e), xbmcgui.NOTIFICATION_ERROR );

	def createPlaylist(self, channelsResp):
		playlistManager = playlist.playlist("pierwszaTV")
		channels = self.getChannelList(channelsResp)
		return playlistManager.getPlaylist(channels)

	def getChannelList(self, channelsResp):
		log.error('PierwszaTV Channels: ' + str(channelsResp))
		jsonChannels = json.loads(channelsResp)
		channels = []
		for channel in jsonChannels['channels']:
			channelName = channel['name']
			channelId = channel['id']
			channelThumb = channel['thumbail']
			channelEpg = channel['epg']
			channels.append(playlist.Media(channelName, channelThumb, 'All', channelId, channelEpg))
		return channels

	def refreshToken(self, streamId, serverId, token, tokenExpireIn):
		try:
			expire = int(tokenExpireIn * 0.75)
			time.sleep(expire)
			params_stream_refresh = 'api_id=' + api_id + '&checksum=' + checksum + '&streamId=' + streamId + '&serverId=' + str(serverId) + '&token=' + token
			query_stream_refresh = {'url': API + 'stream/refresh?' + params_stream_refresh, 'return_data': True, 'use_post': False}
			data_stream_refresh = httpClient.getURLRequestData(query_stream_refresh)
			jsonStreamRefresh = json.loads(data_stream_refresh)
			resfreshStatus = jsonStreamRefresh['status']
			if resfreshStatus == 'ok':
				tokenExpireIn = jsonStreamRefresh['tokenExpireIn']
				#xbmcgui.Dialog().notification("PierwszaTV", "OK: " + str(resfreshStatus) +  " " + str(expire), xbmcgui.NOTIFICATION_ERROR );
				#threading.Thread(target=self.refreshToken, args=(streamId, serverId, token, tokenExpireIn,))
				threading.Thread(target=self.refreshToken, args=(streamId, serverId, token, tokenExpireIn,)).start()
				#tokenThread.setDaemon(True)
				#tokenThread.start()
			#self.kill()
		except Exception as e:
			log.error('PierwszaTV Token Refresh: ' + str(e))
			xbmcgui.Dialog().notification("PierwszaTV Token Refresh:", str(e), xbmcgui.NOTIFICATION_ERROR );
		#else:
			#xbmcgui.Dialog().notification("PierwszaTV", "ERROR: " + str(resfreshStatus), xbmcgui.NOTIFICATION_ERROR );
	def tokenRefresh(self, streamId, serverId, token, tokenExpireIn):
		#xbmcgui.Dialog().notification("PierwszaTV Token Refresh:", str(tokenExpireIn), xbmcgui.NOTIFICATION_ERROR );
		active = True
		delay = 0
		now = datetime.now()
		nextRefresh = now + timedelta(seconds=tokenExpireIn)
		while active == True:
			time.sleep(1)
			now = datetime.now()
			deltaSeconds = (nextRefresh - now).seconds
			#xbmcgui.Dialog().notification("Delta Seconds: ", str(deltaSeconds), xbmcgui.NOTIFICATION_ERROR );
			if deltaSeconds <= 0:
				params_stream_refresh = 'api_id=' + api_id + '&checksum=' + checksum + '&streamId=' + streamId + '&serverId=' + str(serverId) + '&token=' + token
				query_stream_refresh = {'url': API + 'stream/refresh?' + params_stream_refresh, 'return_data': True, 'use_post': False}
				data_stream_refresh = httpClient.getURLRequestData(query_stream_refresh)
				jsonStreamRefresh = json.loads(data_stream_refresh)
				resfreshStatus = jsonStreamRefresh['status']
				if resfreshStatus == 'ok':
					tokenExpireIn = jsonStreamRefresh['tokenExpireIn']
					#xbmcgui.Dialog().notification("PierwszaTV Token Refresh:", str(tokenExpireIn), xbmcgui.NOTIFICATION_ERROR );
					expire = int(tokenExpireIn * 0.75)
					nextRefresh = now + timedelta(seconds=expire)
				else:
					active = False
