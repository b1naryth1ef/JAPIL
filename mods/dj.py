from example import Cmd, client, RequireAdmin, RequireBotOp
import xml.etree.ElementTree as et
import xml.dom.minidom
import random, sys, os

dj_STATUS = False
dj_SPAM = False
dj_USEFILE = False
dj_SONGFILE = None
dj_URL = None
dj_STREAMER = None

settobool = {'on':True, 'off':False}

def todict(string):
	def xmltodict(xmlstring):
		doc = xml.dom.minidom.parseString(xmlstring)
		remove_whilespace_nodes(doc.documentElement)
		return elementtodict(doc.documentElement)
	def elementtodict(parent):
		child = parent.firstChild
		if (not child):
			return None
		elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
			return child.nodeValue
		
		d={}
		while child is not None:
			if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
				try:
					d[child.tagName]
				except KeyError:
					d[child.tagName]=[]
				d[child.tagName].append(elementtodict(child))
			child = child.nextSibling
		return d
	def remove_whilespace_nodes(node, unlink=True):
		remove_list = []
		for child in node.childNodes:
			if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
				remove_list.append(child)
			elif child.hasChildNodes():
				remove_whilespace_nodes(child, unlink)
		for node in remove_list:
			node.parentNode.removeChild(node)
			if unlink:
				node.unlink()
	return xmltodict(string)

def DJ(func):
	def funcy(obj):
		global dj_STATUS
		print dj_STATUS
		if dj_STATUS == True:
			return func(obj)
		else:
			return client.send(obj.chan, 'DJ Plugin is not active.')
	return funcy

@Cmd('!dj', 'Get info about the DJ plugin', '!dj')
@DJ
def cmdDj(obj): pass

@Cmd('!djc', 'Control the DJ plugin', '!djc [command] [data]')
@RequireAdmin
def cmdDjc(obj):
	global dj_STATUS, dj_SPAM, dj_USEFILE, dj_URL
	msg = obj.msg.lower().split(' ')
	if len(msg) == 1:
		client.send(obj.nick, 'Use this to control the bot. Try !djc options for more')
	elif len(msg) == 2:
		if msg[1] == 'options': client.send(obj.nick, 'Controlable options: status, spam, usefile')
		elif msg[1] == 'status': client.send(obj.nick, 'Set the status of the bot. [ON/OFF]')
		elif msg[1] == 'spam': client.send(obj.nick, 'Set if the bot will spam messages. [ON/OFF]')
		elif msg[1] == 'usefile': client.send(obj.nick, 'Set if the bot uses a itunes playlist/library XML file. [ON/OFF]')
		elif msg[1] == 'url': client.send(obj.nick, 'Set the bot\'s stream URL. [URL]')
	elif len(msg) == 3:
		if msg[1] == 'status':
			if msg[2] in settobool: dj_STATUS = settobool[msg[2]]
			else: return client.send(obj.nick, 'Status requires either ON or OFF')
			client.send(obj.nick, 'Set DJ status to %s' % msg[2].upper())
		elif msg[1] == 'spam':
			if msg[2] in settobool: dj_SPAM = settobool[msg[2]]
			else: return client.send(obj.nick, 'Spam requires either ON or OFF')
			client.send(obj.nick, 'Set DJ spam to %s' % msg[2].upper())
		elif msg[1] == 'usefile':
			if msg[2] in settobool: dj_USEFILE = settobool[msg[2]]
			else: return client.send(obj.nick, 'Usefile requires either ON or OFF')
			client.send(obj.nick, 'Set DJ usefile to %s' % msg[2].upper())
		elif msg[1] == 'url':
			if msg[2].startswith('http://'):
				dj_URL = msg[2]
				client.send(obj.nick, 'Set DJ URL to %s' % msg[2])
			else: return client.send(obj.nick, 'URL requires a valid "http://blah.com/stream" URL.')
			
@Cmd('!req', 'Request a song', '!req <song> <artist> [info]')
@DJ
def cmdReq(obj): pass

@Cmd('!song', 'Display the current song', '!song')
@DJ
def cmdSong(obj): pass

@Cmd('!songs', 'List all songs in the library/playlist', '!songs', ['!listsongs', '!allsongs'])
@DJ
def cmdSongs(obj): pass

@Cmd('djurl', 'Get the stream URL', '!djurl')
def cmdUrl(obj):
	if dj_URL != None:
		client.send(obj.chan, 'Stream url: %s' % dj_URL)

def songsSetup():
	if dj_SONGFILE != none:
		x = xmltodict(open(dj_SONGFILE, 'r'))
		y = {}
		keys = []
		for i in x['dict'][0]['dict'][0]['dict']: 
			keys.append(i['string'][0].lower())
			y[i['string'][0].lower()] = (i['string'][0], i['string'][1])

# def parseData(cmd=False, sender=None):
# 	global cData
# 	usock = urllib2.urlopen(url)
# 	dat = usock.read()
# 	usock.close()
# 	if dat:
# 		try:
# 			data = dat.split('<td>Current Song:</td>')[1].split('</td>')[0].replace('\n<td class="streamdata">', '').replace('&amp;', '&')
# 			if data != cData and cmd == False and doLoop == True:
# 				cData = data
# 				api.sendGlobal('Now Streaming [%s]: %s' % (urlz, data))
# 			elif data != cData and cmd == True and sender != None:
# 				cData = data
# 				api.sendGlobal('%s: Current Song is "%s" [%s]' % (sender, data, urlz))
# 		except:
# 			print 'Nop!'
# 			time.sleep(30)

def init():
	while True:
		if dj_SPAM is True and dj_URL != None: pass
		time.sleep(5)
