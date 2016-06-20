# -*- coding: utf-8 -*-

class playlist:

	EXTM3U = "#EXTM3U\n";
	service = None
	channelList = []

	def __init__(self, service):
		self.service = service

	# def init(self, service):
	# 	self.service = service
	def addM3UChannel(self, count, name, thumb, group, id):
		nameStr = unicode(name)
		self.EXTM3U += '#EXTINF:-1, tvg-id="' + str(count)
		self.EXTM3U += '" tvg-name="' + nameStr
		self.EXTM3U += '" tvg-logo="' + str(thumb)
		self.EXTM3U += '" group-title="' + str(group)
		self.EXTM3U += '", ' + nameStr + '\n'
		self.EXTM3U += 'http://localhost:8899/channel?service=' + self.service + '&channel='  + str(id) +'\n\n';
	def getPlaylist(self, channelList):
		count = 0
		for channel in channelList:
			count += 1
			self.addM3UChannel(count, channel.name, channel.thumb, channel.group, channel.id)
		return self.EXTM3U

class Media:
	def __init__(self, name, thumb, group, id, epg):
		self.name = name
		self.id = id
		self.thumb = thumb
		self.group = group
		self.epg = epg