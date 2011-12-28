# JAPIL -- **J**ust **A**nother **P**ython **I**rc **L**ibrary

JAPIL is a simple, easy to use/implement Python IRC Library, with support for the following:

* Decorators
* Threading
* Hooks/Events
* Auto-pong
* And more!

## Example
	
	from irclib import Client, Connection

	conn = Connection(network='irc.quakenet.org') #Create a new connection object. 
	conn.startup() #Start the connection process
	client = Client(conn) #Create a new client object
	client.joinChannel('#nubsybubsy') #Join a channel

	while True:
		client.niceParse() #Starts conn.recv() and parseing lines...
