from example import Cmd, client, RequireAdmin, RequireBotOp
import random, sys, os
from github2.client import Github
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
			self.branches = {branch:''}


		self.old = {}
		self.new = {}

REPOS = [Repo('B1n\'s game', 'So-I-Made-This-Game...', 'b1naryth1ef'), Repo('JAPIL', 'JAPIL', 'b1naryth1ef', 'master')]

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
							client.send(chan, 'New Commit on %s by %s: %s (%s)' % (repo.name, repo.new[i][0].author['name'], repo.new[i][0].message[:50], 'http://github.com/'+repo.new[i][0].url))
					repo.old[i] = repo.new[i]
			time.sleep(45)
