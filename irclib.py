import socket, thread, random, re
import os, sys, time, thread

#LAMBDAZ!
fromHost = lambda host: host.split('!')[0][1:]
modez = {'+':True, '-':False}
hookz = {}
threads = [] #Always keep track of your loose ends! ;)
messgz = {
	'mustbeadmin':'Must be an admin to do that!',
	'botmustbeop':'The bot must be an op to do that!'
}

def Listener(hook):
	def deco(func):
		if hook in hookz: hookz[hook].append(func)
		else: hookz[hook] = [func]
		return func
	return deco

class Data():
	def __init__(self, Type, data):
		self.data = data
		self.type = Type
		self.__dict__.update(data)

def hookFire(hook, data):
	d = Data(hook, data)
	if hook in hookz.keys():
		for i in hookz[hook]:
			threads.append(thread.start_new_thread(i, (d,)))

def niceName(name):
	if name.startswith('@') or name.startswith('+'):
		return name[1:]
	return name

class User():
	def __init__(self, name, c=None, voice=False, op=False):
		if name in c.users.keys():
			self = c.users[name]
		else:
			c.users[niceName(name)] = self
			self.name = name
			self.aliasis = []
			self.voice = voice
			self.op = op
			self.admin = False

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
	def __init__(self, name, c):
		self.name = name
		self.c = c
		self.users = []
		self.topic = ''
		self.modes = {}
		self.penalties = {}

	def hasUser(self, user):
		if user in self.users: return True
		else: return False

	def userNickChanged(self, user, newnick):
		# old = self.users[user]
		# old.changedName(newnick)
		# self.users[newnick] = old
		# del self.users[user]
		self.users.remove(user)
		self.users.append(newnick)
		self.c.users[user].changedName(newnick)
		self.c.users[newnick] = self.c.users[user]
		del self.c.users[user]

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
			self.c.users[user].voice = modez[mode[:1]]
		elif mode[1:] == 'o':
			self.c.users[user].voice = modez[mode[:1]]

	def updateUsers(self, li):
		for i in li:
			if i not in self.users:
				self.users.append(i)
	
	def userPart(self, nick, msg, hostmask):
		print 'User left %s: %s' % (self.name, nick)
		self.users.remove(nick)
	
	def userJoin(self, nick, hostmask):
		print 'User joined %s: %s' % (self.name, nick)
		if nick not in self.c.users:
			self.c.users[nick] = User(nick, self.c)
			self.users.append(nick)

def getUserObj(user, c):
	if user.startswith('+'): return (user[1:], User(user, c, voice=True))
	elif user.startswith('@'): return (user[1:], User(user, c, voice=True, op=True))
	else: return (user, User(user, c))

def updateList(li, c):
	lm = []
	for user in li:
		lm.append(getUserObj(user, c)[0])
	return lm

class Connection():
	'''Wrapper around socket object'''
	def __init__(self, network='irc.freenode.net', port=6667, nick='Exampl3B0t', startchannels=['#bitchnipples'], tag='irclib'):
		self.getRandTag = lambda x: '%s_%s' % (x, random.randint(1111,9999))

		self.network = network
		self.port = port
		self.nick = nick
		self.startchannels = startchannels
		self.tag = tag
		self.alive = False

		self.surv = self.getRandTag(tag)
		self.host = self.getRandTag(tag)
		self.real = self.getRandTag(tag)

		self.c = None #Block out the socket object

	def disconnect(self):
		self.c.close
		self.alive = False

	def startup(self, ret=False):
		self.connect()
		self.join()
		if ret is True: return self

	def connect(self):
		self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.c.connect((self.network, self.port))
		self.alive = True
	   
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
		self.c.send('JOIN '+str('#l33tb0tbr0ski')+'\r\n') #This message is made to get lost.
		while True:
			x = self.c.recv(1024).strip()
			if 'End of /MOTD' in x:
				return True

	def recv(self, bytes=1024): 
		if self.alive is True:
			return self.c.recv(bytes)	
		else:
			return None
	def write(self, content): self.c.send('%s\r\n' % content)

class Client():
	'''The actual IRC client, wrapped around the Connection class'''
	def __init__(self, connection, rejoin=True):
		self.c = connection
		self.channels = {}
		self.badchannels = []
		self.users = {}
		self.nick = self.c.nick
		self.rejoin = rejoin

		self.autoPong = True
		self.botMode = False
		self.botPrefix = '!'
		self.maxLength = 100 #The max length a line can be
		self.printLines = True

		self.messages = messgz

	def opUser(self, user, channel=None):
		i = []
		if channel is None:
			for chan in self.channels:
				if user in self.channels.users:
					i.append(user)
			if len(i) == 1:
				channel = i[0]
			else:
				return False
		self.sendRaw('MODE %s +o %s' % (channel, user))
		return True
	
	def niceList(self, seq, length=None):
		'''Make a nice list!'''
		if not length:
			length = self.maxLength
		ret = [seq[i:i+length] for i in range(0, len(seq), length)]
		return ret
			 
	def send(self, chan, msg):
		if len(msg) > 100:
			for i in niceList(msg, 100):
				self.sendRaw('PRIVMSG %s :%s' % (chan, i))
		elif len(msg) <= 100:
			self.sendRaw('PRIVMSG %s :%s' % (chan, msg))
	
	def sendRaw(self, raw): self.c.write(raw)
	
	def quit(self, msg='B1naryth1ef Rocks!', full=True):
		self.c.write('QUIT :%s' % msg)
		if full is True: self.c.disconnect()

	def canJoin(self, channel):
		if channel not in self.channels.keys() and channel not in self.badchannels:
			return True
		return False
	
	def isClientOp(self): return self.users[self.nick].op

	def inChannel(self, channel):
		if channel in self.channels.keys():
			return True
		return False

	def joinChannel(self, channel, passwd=''):
		self.c.write('JOIN %s %s' % (channel, passwd))
		self.channels[channel] = Channel(channel, self)
	
	def partChannel(self, channel, msg='G\'bye!'):
		self.c.write('PART %s :%s' % (channel, msg))
		del self.channels[channel]

	def setUserMode(self, user, channel, mode): pass
	def setChanMode(self, channel, mode): pass

	def niceParse(self):
		self.parse(self.c.recv())
	
	def makeAdmin(self, nick):
		x = False
		if nick in self.users.keys():
			self.users[nick].admin = True
			x = True
		elif '@'+nick in self.users.keys():
			self.users['@'+nick].admin = True
			x = True
		elif '+'+nick in self.users.keys():
			self.users['+'+nick].admin = True
			x = True
		return x

	def removeAdmin(self, nick):
		if nick in self.users.keys():
			self.users[nick].admin = False
			return True
		return False

	def isAdmin(self, nick):
		if niceName(nick) in self.users.keys():
			if self.users[nick].admin is True:
				return True
		return False

	def sendMustBeAdmin(self, chan):
		self.send(chan, self.messages['mustbeadmin'])	
	def sendClientMustBeOp(self, chan):
		self.send(chan, self.messages['botmustbeop'])	 

	def parse(self, inp):
		def names(msg):
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[4]
			users = msg[2].split(' ')
			self.channels[chan].updateUsers(updateList(users, self))
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
			if nick != self.nick:
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
			if chan == self.nick:
				chan = nick
				hookFire('privsay', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan})
			else:
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

		def who(line):
			'''/WHO Response'''
			msg = line.split(' ')
			name = msg[4][1:]
			hostmask = msg[5]
			nick = msg[7]
			hookFire('who_response', {'name':name, 'hostmask':hostmask, 'nick':nick})

		def pong(line):
			'''Ping request'''
			if self.autoPong is True: self.c.write('PONG')
			hookFire('ping', {'line':line})
		if inp != None:
			inp = inp.split('\r\n')
		else:
			return None
		for l in inp:
			if self.printLines is True: print '[X]',l
			line_type = l.strip().split(' ')
			line = l.strip()
			orig = l
			if len(line_type) >= 2:
				if line_type[1] == 'PRIVMSG': msg(line)
				elif line_type[0] == 'PING': pong(line)
				elif line_type[1] == '353': names(line)
				elif line_type[1] == '332': topic(line)
				elif line_type[1] == '352': who(line)
				elif line_type[1] == 'PART': part(line)
				elif line_type[1] == 'JOIN': join(line)
				elif line_type[1] == 'MODE': mode(line)
				elif line_type[1] == 'TOPIC': setTopic(line)
				elif line_type[1] == 'KICK': kick(line)
				elif line_type[1] == 'NICK': nick(line)
				elif orig.find('\x01'): print True
			
