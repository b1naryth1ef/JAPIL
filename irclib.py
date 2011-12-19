import socket, thread, random, re
import os, sys, time

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
	
	def updateUsers(self, dic):
		self.users.update(dic)

def updateList(li):
	lm = {}
	for user in li:
		if user.startswith('+'): lm[user[1:]] = User(user, voice=True)
		elif user.startswith('@'): lm[user[1:]] = User(user, voice=True, op=True)
		else: lm[user] = User(user)
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
			print self.channels[chan].users['Q'].op

		def topic(msg):
			#:servercentral.il.us.quakenet.org 332 Exampl3B0t #bitchnipples :Welcome to BITCHNIPPLES CLAN! We apologize for the inconvenience... http://www.reddit.com/r/AskReddit/comments/nfjlo/i_think_i_may_be_addicted_to_having_sex_with_my/
			msg = msg.split(':', 2)
			chan = msg[1].split(' ')[3]
			topic = msg[2]
			print chan,topic

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
				# elif line_type[1] == '366':
				# 	print 'End of names!'
				elif line_type[1] == '332':
					topic(line)


