import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcaddon
import xbmcplugin
import pierwszaTV

API = pierwszaTV.pierwszaTV()

addon = xbmcaddon.Addon()
sortType = addon.getSetting('pierwsza_tv_sort');

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def getChannels():
		channels = API.getChannels()
		listing = []
		for channel in channels:
			channelThumb = API.baseUrl + str(channel.thumb)
			title = '[COLOR green]' + channel.name + '[/COLOR]'
			if channel.epg != None:
				title += ' ( ' + channel.epg + ' )'
			list_item = xbmcgui.ListItem(label=title, thumbnailImage=channelThumb)
			list_item.setProperty('fanart_image', channelThumb)
			list_item.setInfo('video', {'title': title, 'genre': channel.group})
			list_item.setArt({'landscape': channelThumb})
			list_item.setProperty('IsPlayable', 'true')
			url = '{0}?action=play&video={1}'.format(_url, str(channel.id))
			is_folder = False
			listing.append((url, list_item, is_folder))
		xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
		if sortType == "1":
			xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
		xbmcplugin.endOfDirectory(_handle)

def play_video(path):
		channelUrl = API.getChannel(path)
		if path != None:
			play_item = xbmcgui.ListItem(path=channelUrl)
		xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def router(paramstring):
		params = dict(parse_qsl(paramstring))
		# Check the parameters passed to the plugin
		if params:
				if params['action'] == 'listing':
						# Display the list of videos in a provided category.
						list_videos(params['category'])
				elif params['action'] == 'play':
						# Play a video from a provided URL.
						play_video(params['video'])
		else:
				getChannels()


if __name__ == '__main__':
		router(sys.argv[2][1:])
