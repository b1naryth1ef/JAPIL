from example import Cmd, client
from subprocess import *

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
'Time to go trolololol in bot heaven']

@Cmd('!version', 'Print-out the latest version of the bot (from the git header)', '!version', ['!ver'])
def version(msg):
	p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)
	commit = p.stdout.readline()
	author = p.stdout.readline()
	date = p.stdout.readline()
	#client.send(msg.chan, 'Version: '+str(api.getVersion()))
	client.send(msg.chan, "Git: "+commit)
	client.send(msg.chan, author)
	client.send(msg.chan, date)

@Cmd('!channels', 'List the channels the bot is currently in', '!channels', ['!chans'])
def chans(msg):
	li = []
	for channel in clients.c.channels:
		li.append(channel.name)
	say = client.niceList(li)
	client.send(msg.chan, 'Channels I\'m currently in:')
	for line in say:
		client.send(msg.chan, line)
