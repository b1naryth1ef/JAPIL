import socket, thread, random, re
import os, sys, time

#LAMBDAZ!
fromHost = lambda host: host.split('!')[0][1:]
modez = {'+':True, '-':False}

class User():
	def __init__(self, name, voice=False, op=False):
		self.name = name
		self.voice = voice
		self.op = op

class Channel():
	def __init__(self, name):
		self.name = name
		self.users = {}
		self.topic = ''
		self.modes = {}
	
	def setMode(self, mode, user): 
		self.modes[mode[1:]] = modez[mode[:1]]

	def setUserMode(self, mode, user, byuser): 
		if mode[1:] == 'v':
			self.users[user].voice = modez[mode[:1]]
		if mode[1:] == 'o':
			self.users[user].voice = modez[mode[:1]]

	def updateUsers(self, dic):
		self.users.update(dic)
	
	def userPart(self, nick, msg, hostmask):
		print 'User left: %s' % nick
		del self.users[nick]
	
	def userJoin(self, nick, hostmask):
		print 'User joined: %s' % nick
		self.users[nick] = User(nick)

def getUserObj(user):
	if user.startswith('+'): return (user[1:], User(user, voice=True))
	elif user.startswith('@'): return (user[1:], User(user, voice=True, op=True))
	else: return (user, User(user))

def updateList(li):
	lm = {}
	for user in li:
		x = getUserObj(user)
		lm[x[0]] = x[1]
	return lm

class Connection():
	def __init__(self, network='irc.freenode.net', port=6667, nick='Exampl3B0t', startchannels=['#bitchnipples'], tag='irclib'):
		self.getRandTag = lambda x: '%s_%s' % (x, random.randint(1111,9999))

		self.network = network
		self.port = port
		self.nick = nick
		self.startchannels = startchannels
		self.tag = tag

		self.surv = self.getRandTag(tag)
		self.host = self.getRandTag(tag)
		self.real = self.getRandTag(tag)

	def startup(self, ret=False):
		self.connect()
		self.join()
		if ret is True: return self

	def connect(self):
		self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.c.connect((self.network, self.port))
	   
	def join(self):
		self.c.send('NICK '+str(self.nick)+'\r\n')
		self.c.send('USER %s 0 * :Py Guy\r\n' % (self.nick))
		while True:
			x = self.c.recv(1024).strip()
			if 'PING' in x:
				time.sleep(2)
				#print "'",x[1].strip(' ').strip(' '),"'"
				self.c.send('PONG '+x.split('PING')[1].strip(' ').strip(' '))
				break
		self.c.send('JOIN '+str('#l33tb0tbr0ski')+'\r\n') #This message is made to get lost...
		while True:
			x = self.c.recv(1024).strip()
			if 'End of /MOTD' in x:
				return True
		
	def disconnect(self): 
		self.c.close()

	def recv(self, bytes=1024): return self.c.recv(bytes)	
	def write(self, content):
		self.c.send('%s\r\n' % content)

class Client():
	def __init__(self, connection):
		self.c = connection
		self.channels = {}
	
	def quit(self, msg='B1naryth1ef Rocks!', full=True):
		self.c.write('QUIT :%s' % msg)
		if full is True: self.c.disconnect()

	def joinChannel(self, channel, passwd=''):
		self.c.write('JOIN %s %s' % (channel, passwd))
		self.channels[channel] = Channel(channel)
	
	def partChannel(self, channel, msg='G\'bye!'):
		self.c.write('PART %s :%s' % (channel, msg))

	def parse(self, inp):
		def names(msg):
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[4]
			users = msg[2].split(' ')
			self.channels[chan].updateUsers(updateList(users))

		def topic(msg):
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[3]
			topic = msg[2]
		
		def part(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			pmsg = msg[3][1:]
			nick = fromHost(hostmask)
			self.channels[chan].userPart(nick, pmsg, hostmask)

		def join(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			nick = fromHost(hostmask)
			self.channels[chan].userJoin(nick, hostmask)
		
		def mode(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			fromuser = fromHost(hostmask)
			if len(msg) == 4: #Channel Mode
				mode = msg[3]
				self.channels[chan].setMode(mode, fromuser)
			elif len(msg) == 5: #User Mode
				touser = msg[4]
				mode = msg[3]
				self.channels[chan].setUserMode(mode, touser, fromuser)
				print 'FIRED'

		def setTopic(msg): pass

		inp = inp.split('\r\n')
		for l in inp:
			print '[X]',l
			line_type = l.strip().split(' ')
			line = l.strip()
			if len(line_type) >= 2:
				if line_type[1] == 'PRIVMSG':
					print 'Private Message!'
				elif line_type[1] == '353':
					names(line)
				elif line_type[1] == '332':
					topic(line)
				elif line_type[1] == 'PART':
					part(line)
				elif line_type[1] == 'JOIN':
					join(line)
				elif line_type[1] == 'MODE':
					mode(line)
				elif line_type[1] == 'TOPIC':
					setTopic(line)


