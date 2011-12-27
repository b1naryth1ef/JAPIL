from irclib import Connection, Client, Listener
import thread

mods = ['default']

threads = []
aliass = {}
commands = {}

class Command():
	def __init__(self, cmd, exe, desc, usage, alias):
		self.cmd = cmd
		self.desc = desc
		self.usage = usage
		self.alias = alias
		self.exe = exe

		for i in self.alias:
			aliass[i] = cmd

def Cmd(cmd, desc, usage, alias=[]):
	def deco(func):
		print 'Called'
		commands[cmd] = Command(cmd, func, desc, usage, alias)
		return func
	return deco
	
@Listener('command')
def cmdParser(obj):
	i = obj.msg.split(' ')[0]
	print 'Command Fire: %s' % i
	if i in commands:
		threads.append(thread.start_new_thread(commands[i].exe, (obj,)))
	elif i in aliass:
		threads.append(thread.start_new_thread(commands[aliass[i]].exe, (obj,)))

def loop():
	while True:
		client.parse(conn.recv())

def init():
	global conn, client
	conn = Connection(network='irc.quakenet.org').startup(True)
	client = Client(conn)
	client.joinChannel('#bitchnipples')
	client.botMode = True

	for i in mods:
		__import__('mods.'+i)
	
	loop()
