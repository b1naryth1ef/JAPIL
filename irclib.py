import socket, thread, random, re
import os, sys, time, thread

#LAMBDAZ!
fromHost = lambda host: host.split('!')[0][1:]
modez = {'+':True, '-':False}
hookz = {}
threads = []

def Listener(hook):
	def deco(func):
		if hook in hookz: hookz[hook].append(func)
		else: hookz[hook] = [func]
		return func
	return deco

class Data():
	def __init__(self, data):
		self.data = data
		self.__dict__.update(data)

def hookFire(hook, data):
	d = Data(data)
	if hook in hookz.keys():
		for i in hookz[hook]:
			threads.append(thread.start_new_thread(i, (d,)))

class User():
	def __init__(self, name, voice=False, op=False):
		self.name = name
		self.aliasis = []
		self.voice = voice
		self.op = op

	def changedName(self, newname):
		self.aliasis.append(self.name)
		self.name = newname

class Penalty():
	def __init__(self, user, reason, byuser, Type):
		self.user = user #user OR hostmask
		self.reason = reason
		self.byuser = byuser
		self.type = Type
		self.time = time.time()
		self.enabled = True

class Channel():
	def __init__(self, name):
		self.name = name
		self.users = {}
		self.topic = ''
		self.modes = {}
		self.penalties = {}

	def hasUser(self, user):
		if user in self.users.keys(): return True
		else: return False

	def userNickChanged(self, user, newnick):
		old = self.users[user]
		old.changedName(newnick)
		self.users[newnick] = old
		del self.users[user]

	def addPenalty(self, user, penalty):
		if user in self.penalties.keys(): self.penalties[user].append(penalty)
		else: self.penalties[user] = [penalty]

	def userKicked(self, user, byuser, reason):
		self.addPenalty(user, Penalty(user, None, reason, byuser, 'kick'))

	def setTopic(self, topic, user):
		self.topic = topic
	
	def setMode(self, mode, user): 
		self.modes[mode[1:]] = modez[mode[:1]]

	def setUserMode(self, mode, user, byuser): 
		if mode[1:] == 'b' and mode[1:] == '+':
			self.addPenalty(user, Penalty(user, reason, byuser, 'ban'))
		elif mode[1:] == 'b' and mode[1:] == '+':
			self.penalties[user].enabled = False
		elif mode[1:] == 'v':
			self.users[user].voice = modez[mode[:1]]
		elif mode[1:] == 'o':
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
	def __init__(self, connection, rejoin=True):
		self.c = connection
		self.channels = {}
		self.nick = self.c.nick
		self.rejoin = rejoin

		self.autoPong = True
		self.botMode = False
		self.botPrefix = '!'
	
	def quit(self, msg='B1naryth1ef Rocks!', full=True):
		self.c.write('QUIT :%s' % msg)
		if full is True: self.c.disconnect()

	def joinChannel(self, channel, passwd=''):
		self.c.write('JOIN %s %s' % (channel, passwd))
		self.channels[channel] = Channel(channel)
	
	def partChannel(self, channel, msg='G\'bye!'):
		self.c.write('PART %s :%s' % (channel, msg))
		del self.channels[channel]

	def setUserMode(self, user, channel, mode): pass
	def setChanMode(self, channel, mode): pass

	def parse(self, inp):
		def names(msg):
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[4]
			users = msg[2].split(' ')
			self.channels[chan].updateUsers(updateList(users))
			hookFire('names', {'nicks':users, 'chan':chan})

		def topic(msg):
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[3]
			topic = msg[2]
			hookFire('topic', {'chan':chan, 'topic':topic})
		
		def part(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			pmsg = msg[3][1:]
			nick = fromHost(hostmask)
			self.channels[chan].userPart(nick, pmsg, hostmask)
			hookFire('part', {'hostmask':hostmask, 'nick':nick, 'msg':pmsg, 'chan':chan})

		def join(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			nick = fromHost(hostmask)
			self.channels[chan].userJoin(nick, hostmask)
			hookFire('join', {'hostmask':hostmask, 'chan':chan, 'nick':nick})
		
		def mode(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			fromuser = fromHost(hostmask)
			if msg[2] == self.nick: pass
			elif len(msg) == 4: #Channel Mode
				mode = msg[3]
				if fromuser != mode:
					self.channels[chan].setMode(mode, fromuser)
					hookFire('channelmode', {'hostmask':hostmask, 'fromnick':fromuser, 'mode':mode})
			elif len(msg) >= 5: #User Mode
				touser = msg[4]
				mode = msg[3]
				self.channels[chan].setUserMode(mode, touser, fromuser)
				hookFire('usermode', {'fromnick':fromuser, 'tonick':touser, 'mode':mode, 'chan':chan})

		def setTopic(msg):
			msg = msg.split(' ', 3)
			hostmask = msg[0]
			chan = msg[2]
			newtopic = msg[3][1:]
			nick = fromHost(hostmask)
			self.channels[chan].setTopic(newtopic, nick)
			hookFire('settopic', {'hostmask':hostmask, 'nick':nick, 'newtopic':newtopic})
		
		def msg(msg):
			msg = msg.split(' ', 3)
			hostmask = msg[0]
			chan = msg[2]
			msg = msg[3][1:]
			nick = fromHost(hostmask)
			print '[%s] %s: %s' % (chan, nick, msg)
			hookFire('chansay', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan})
			if self.botMode is True and msg.startswith(self.botPrefix):
				hookFire('command', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan})
		
		def kick(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			chan = msg[2]
			fromnick = fromHost(hostmask)
			nick = msg[3]
			reason = msg[4][1:]
			if reason == nick:
				reason = 'none given'
			if self.nick == nick:
				hookFire('uskicked', {'chan':chan, 'fromnick':fromnick})
				del self.channels[chan]
				if self.rejoin is True:
					self.joinChannel(chan)
			else:
				self.channels[chan].userKicked(nick, fromnick, reason)
				hookFire('kick', {'fromnick':fromnick, 'nick':nick, 'chan':chan, 'reason':reason})

		def nick(msg):
			msg = msg.split(' ')
			hostmask = msg[0]
			fromnick = fromHost(hostmask)
			tonick = msg[2][1:]
			for chan in self.channels.values():
				if chan.hasUser(fromnick):
					chan.userNickChanged(fromnick, tonick)
			hookFire('nick_change', {'hostmask':hostmask, 'fromnick':fromnick, 'tonick':tonick})

		inp = inp.split('\r\n')
		for l in inp:
			print '[X]',l
			line_type = l.strip().split(' ')
			line = l.strip()
			orig = l
			if len(line_type) >= 2:
				if line_type[1] == 'PRIVMSG':
					msg(line)
				elif line_type[0] == 'PING' and self.autoPong is True:
					self.c.write('PONG')
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
				elif line_type[1] == 'KICK': 
					kick(line)
				elif line_type[1] == 'NICK':
					nick(line)
				elif orig.find('\x01'):
					print True
			
