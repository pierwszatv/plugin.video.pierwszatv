# -*- coding: utf-8 -*-
import os, sys
import playlist
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
import httpCommon
import pLog
import json
#reload(sys)
#sys.setdefaultencoding('utf-8')

API = "http://www.telewizjada.net/"
ptv = xbmcaddon.Addon()
httpClient = httpCommon.common()
log = pLog.pLog()

epgMapping = {"TV4": "TV 4","Super Stacja": "Superstacja","TV6": "TV 6","Ale Kino+": "ale kino+", "FilmBox": "Filmbox","FilmBox Action": 
				"Filmbox Action","HBO 2": "HBO2","Sci Fi": "SciFi Universal","Universal Channel": "Universal HD", "Eleven Sport": "Eleven Sports",
				"MiniMini+": "Minimini+","Discovery": "Discovery Channel", "National Geographic": "National Geographic Channel"}

class telewizjada:

	baseUrl = API

	def __init__(self):
		self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "telewizjada.cookie"
		pass
	def getStreamUrl(self, channel):
		return self.urlStream
	def getChannel(self, channel):
		try:
			query_mainchannel = {'url': API + 'get_mainchannel.php', 'return_data': True, 'use_post': True}
			data_mainchannel = httpClient.getURLRequestData(query_mainchannel, {'cid' : str(channel)})
			result_mainchannel = json.loads(data_mainchannel)
			urlChannel = result_mainchannel['url']
			query_set_cookie = {'url': API + 'set_cookie.php', 'use_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIEFILE, 'return_data': False, 'use_post': True}
			httpClient.getURLRequestData(query_set_cookie, {'url' : str(urlChannel)})
			query_data_channel = {'url': API + 'get_channel_url.php', 'use_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIEFILE, 'return_data': True, 'use_post': True}
			result_data_channel = httpClient.getURLRequestData(query_data_channel, {'cid' : str(channel)})
			jsonChannelUrl = json.loads(result_data_channel)
			channelUrl = jsonChannelUrl['url']
			query_data_m3u = {'url': channelUrl, 'use_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIEFILE, 'return_data': True, 'use_post': False}
			result_m3u_data = httpClient.getURLRequestData(query_data_m3u)
			chunklist_value = '';
			streamUrl = '';
			for line in str(result_m3u_data).split('\n'):
				if 'chunklist' in line:
					chunklist_value = line
			streamUrl = channelUrl.replace('playlist.m3u8', chunklist_value)
			self.urlStream = streamUrl
			return streamUrl
		except Exception as e:
			log.error('Telewizjada: ' + str(e))
			xbmcgui.Dialog().notification("Telewizjada", str(e), xbmcgui.NOTIFICATION_ERROR );

	def getChannelsM3U(self):
		try:
			getChannelsReq = {'url': API + 'get_channels.php', 'return_data': True, 'use_post': True}
			getChannelsResp = httpClient.getURLRequestData(getChannelsReq)
			if getChannelsResp != None:
				return self.createPlaylistM3U(getChannelsResp)
				#return getChannelsResp
		except Exception as e:
			log.error('Telewizjada: ' + str(e))
			xbmcgui.Dialog().notification("Telewizjada", str(e), xbmcgui.NOTIFICATION_ERROR );
		return "M3U_Content"

	def getChannels(self):
		try:
			getChannelsReq = {'url': API + 'get_channels.php', 'return_data': True, 'use_post': True}
			getChannelsResp = httpClient.getURLRequestData(getChannelsReq)
			if getChannelsResp != None:
				return self.getChannelList(getChannelsResp)
		except Exception as e:
			log.error('Telewizjada: ' + str(e))
			xbmcgui.Dialog().notification("Telewizjada", str(e), xbmcgui.NOTIFICATION_ERROR );

	def createPlaylistM3U(self, channelsResp):
		playlistManager = playlist.playlist("telewizjada")
		channels = self.getChannelList(channelsResp)
		return playlistManager.getPlaylist(channels)

	def getChannelList(self, channelsResp):
		jsonChannels = json.loads(channelsResp)
		channels = []
		for cat in jsonChannels['categories']:
			catId = cat['Categoryid']
			catName = cat['Categoryname']
			#log.error('Telewizjada: ' + catName)
			#categoryMap[str(catId)] = catName
			channelList = cat['Categorychannels']
			for singleChannel in channelList:
				#count += 1
				channelId = singleChannel['id']
				channelName = singleChannel['displayName']
				#log.error('Telewizjada: ' + channelName)
				if channelName in epgMapping:
					channelName = epgMapping[channelName]
				channelThumb = singleChannel['thumb']
				channels.append(playlist.Media(channelName, channelThumb, catName, channelId))
		return channels