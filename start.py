import example, urllib2

f = urllib2.urlopen('http://bella.wbbmx.org/japil/updates')
if float(f.read(10)) > example.version:
	print 'There is an newer version!'
	print 'Download it at https://github.com/b1naryth1ef/JAPIL/zipball/release'
else:
	print 'No newer versions found!'
example.init()