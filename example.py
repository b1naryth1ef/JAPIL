from irclib import Connection, Client, Listener

conn = Connection(network='irc.quakenet.org').startup(True)
client = Client(conn)
client.joinChannel('#bitchnipples')
client.botMode = True

@Listener('command')
def cmdParser(obj):
	print 'Got Command Broski!'

while True:
	client.parse(conn.recv())
