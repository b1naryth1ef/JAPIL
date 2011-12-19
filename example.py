from irclib import Connection, Client

conn = Connection(network='irc.quakenet.org').startup(True)
client = Client(conn)
client.joinChannel('#bitchnipples')

while True:
	client.parse(conn.recv())
