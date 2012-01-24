from example import Cmd, client, RequireAdmin, RequireBotOp
import random, sys, os
from github2.client import Github
from github2.request import HttpError
import re, time
from configz import githubKEY

github = Github(username="B1narysB0t", api_token=githubKEY)
CHANS = ['#bitchnipples', '#b1naryth1ef']

class Repo():
	def __init__(self, name, actual_name, owner, branch='all'):
		self.name = name
		self.repo = actual_name
		self.owner = owner
		
		self.url = '%s/%s' % (owner, actual_name)

		if branch is 'all':
			self.branches = github.repos.branches(self.url)
		else:
			self.branches = {}
			for i in branch:
				self.branches[i] = ''

		self.old = {}
		self.new = {}

def isFork(booly):
	if booly is True:
		return ' [FORK]'
	else:
		return ''

REPOS = [Repo('B1n\'s game', 'So-I-Made-This-Game...', 'b1naryth1ef'), Repo('JAPIL', 'JAPIL', 'b1naryth1ef', ['master']), Repo('UrTBot', 'UrTBot', 'b1naryth1ef')]

@Cmd('!repos', 'List a github users repos', '!repos <github user>')
def cmdUserListRepo(obj):
	msg = obj.msg.split(' ')
	if len(msg) == 2:
		try:
			repos = github.repos.list(msg[1])
		except HttpError, e:
			return client.send(obj.chan, 'User %s is not on Github (Misspelled?)' % msg[1])
		if len(repos) >= 1:
			client.send(obj.chan, 'Repositories for %s: %s' % (msg[1], ', '.join([i.name for i in repos[:10]])))
		else:
			client.send(obj.chan, 'No repositories for user %s' % msg[1])
	else:
		 client.send(obj.chan, 'Usage: ', cmdUserListRepo.usage)

@Cmd('!repo', 'Get info about a specific repository', '!repo <user/repo> ')
def cmdRepoInfo(obj):
	msg = obj.msg.split(' ')
	if len(msg) == 2:
		if not '/' in msg[1]:
			return client.send(obj.chan, 'Usage: %s (remember /)' % cmdRepoInfo.usage)
		try:
			repo = github.repos.show(msg[1])
		except:
			return client.send(obj.chan, 'Unknown user/repo (Misspelled?)')
		client.send(obj.chan, '%s%s: %s (%s)' % (repo.name, isFork(repo.fork), repo.description, repo.url))
	else:
		 client.send(obj.chan, 'Usage: ', cmdRepoInfo.usage)

def gity(lin):
	return 'http://github.com/'+str(lin)

def init():
	for repo in REPOS:
		for branch in repo.branches.keys():
			repo.old[branch] = github.commits.list(repo.url, branch)
	while True:
		for repo in REPOS:
			for i in repo.branches.keys():
				repo.new[i] = github.commits.list(repo.url, i)
				if len(repo.old[i]) != 0 and len(repo.new[i]) != 0:
					if repo.new[i][0].tree != repo.old[i][0].tree:
						for chan in CHANS:
							client.send(chan, 'New Commit on %s\%s by %s: %s (%s)' % (repo.name, i, repo.new[i][0].author['name'], repo.new[i][0].message[:50], gity(repo.new[i][0].url)))
					repo.old[i] = repo.new[i]
			time.sleep(45)
