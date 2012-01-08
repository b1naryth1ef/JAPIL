from example import Cmd, client, RequireAdmin
from subprocess import *
import random, sys, os

byelist = ["I'm gonna go party somewhere else...", 
'Peace YO!', 
'Gotta go tell Neek to stop having such loud sex.', 
'lmfao brb ttylijos', 
'I wonder what this button does...', 
'Fonducci what are you doing? NO WAIT DONT TOUCH TH-', 
"Java? Oh lemme just killl myself then...",
'from main import FuckYouGuys',
'class Neek(OldMan.Balls): return lame',
'while Afro: print "racist"',
"G'BYE YOU NUBSERS!",
'LOLLY! DONT POINT THAT GUN TH-',
'Time to go trololololing in bot heaven',
'Can\' touch this!']

@Cmd('!version', 'Print-out the latest version of the bot (from the git header).', '!version', ['!ver'])
def version(msg):
	p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)
	commit = p.stdout.readline()
	author = p.stdout.readline()
	date = p.stdout.readline()
	#client.send(msg.chan, 'Version: '+str(api.getVersion()))
	client.send(msg.chan, "Git: "+commit)
	client.send(msg.chan, author)
	client.send(msg.chan, date)

@Cmd('!quit', 'Nicely exit irc.', '!quit [goodbye message]', ['!q'])
@RequireAdmin
def quit(msg):
	#!quit blah blah blah
	msgz = msg.msg.split(' ', 1)
	cli = msg.nick
	if len(msgz) == 1:
		client.quit(random.choice(byelist))
	elif len(msgz) == 2:
		client.quit(msgz[1])
	sys.exit() #For now

@Cmd('!1337', 'For testing usage only!', '!1337', ['!l33t'])
def l33t(msg):
	print 'Making admin:',client.makeAdmin(msg.nick)

@Cmd('!addadmin', 'Add an admin.', '!addadmin <user>')
@RequireAdmin
def addAdmin(msg):
	msz = msg.msg.split(' ')
	if len(msz) == 2:
		if client.makeAdmin(msz[1]): client.send(msg.chan, 'Added %s as an admin' % msz[1])
		else: client.send(msg.chan, 'Unknown user %s' % msz[1])
	else: client.send(msg.chan, 'Usage: ', addAdmin.usage)

@Cmd('!rmvadmin', 'Remove an admin.', '!rmvadmin <user>')
@RequireAdmin
def rmvAdmin(msg):
	msz = msg.msg.split(' ')
	if len(msz) == 2:
		if client.removeAdmin(msz[1]): client.send(msg.chan, 'Removed %s as an admin' % msz[1])
		else: client.send(msg.chan, 'Unknown user %s' % msz[1])
	else: client.send(msg.chan, 'Usage: ', rmvAdmin.usage)

@Cmd('!join', 'Join a channel.', '!join <channel>')
@RequireAdmin
def joinChan(msg):
	msz = msg.msg.split(' ')
	if len(msz) == 2:
		if client.canJoin(msz[1]):
			client.joinChannel(msz[1])
			client.send(msg.chan, 'Joined channel %s' % msz[1])
		else: client.send(msg.chan, 'Can\'t join channel %s. (Blocked or already in it...)' % msz[1])
	else: client.send(msg.chan, 'Usage: ', joinChan.usage)

@Cmd('!part', 'Part (leave) a channel', '!part <channel> [msg]')
@RequireAdmin
def partChan(msg):
	msz = msg.msg.split(' ')
	if len(msz) in [2,3]:
		if len(msz) == 3: m = msz[2]
		else: m = random.choice(byelist)
		if client.inChannel(msz[1]):
			client.partChannel(msz[1], m)
			client.send(msg.chan, 'Parted channel %s' % msz[1])
		else: client.send(msg.chan, 'Can\'t part channel %s, not in it.' % msz[1])
	else: client.send(msg.chan, 'Usage: ', partChan.usage)


