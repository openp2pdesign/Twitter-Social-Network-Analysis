# -*- encoding: utf-8 -*-
#
# Social Network Analysis of a Twitter list members friendships
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: GPL v.3
#
# Requisite: 
# install twitter with pip install twitter
# install NetworkX with pip install networkx
#
# Other Twitter libraries: https://dev.twitter.com/docs/twitter-libraries
#

from twitter import *
import networkx as nx
from time import sleep
import sys
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.DiGraph()
username = "openp2pdesign"
errors = 0
connections = {}

print ""
print "....................................................."
print "FRIENDSHIPS WITHIN A TWITTER LIST OF:",username
print ""	

def load_connections(user_list,option):
	for i in user_list:
		print ""
		if option == "followers":
			print "Loading users who follow",i,"..."
		else:
			print "Loading users whom",i,"follows..."
		query = {}
		counting = 0
		cursor = -1
		connections[i] = []

		while cursor != "0":
			# API: https://dev.twitter.com/docs/api/1.1/get/friends/ids
			try:
				if option == "followers":
					query = twitter.followers.ids(user_id=i,count=5000,cursor=cursor)
				else:
					query = twitter.friends.ids(user_id=i,count=5000,cursor=cursor)
				cursor = query["next_cursor_str"]
				for id in query["ids"]:
					connections[i].append(id)
					print " - ",id
			except Exception,e:
				if "Rate limit exceeded" in str(e):
					print "Rate exceeded... waiting 15 minutes before retrying"
				
					# Countdown http://stackoverflow.com/questions/3249524/print-in-one-line-dynamically-python
					for k in range(1,60*15):
						remaining = 60*15 - k
						sys.stdout.write("\r%d seconds remaining   " % remaining)
						sys.stdout.flush()
						sleep(1)
					sys.stdout.write("\n")
					
					if option == "followers":
						query = twitter.followers.ids(user_id=i,count=5000,cursor=cursor)
					else:
						query = twitter.friends.ids(user_id=i,count=5000,cursor=cursor)
					cursor = query["next_cursor_str"]
					for id in query["ids"]:
						connections[i].append(id)
						print " - ",id
				elif "Not authorized" in str(e):				
					print "There were some errors with user",i,"... most likely it is a protected user"
					cursor = "0"
					errors += 1
				else:
					print "Some error happened with user",i
					cursor = "0"
					errors += 1
	return connections

# Get them from http://dev.twitter.com
OAUTH_TOKEN = "Insert here"
OAUTH_SECRET = "Insert here"
CONSUMER_KEY = "Insert here"
CONSUMER_SECRET = "Insert here"

# Log in
auth = OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter = Twitter(auth = auth)

# Load lists of the user
# API: https://dev.twitter.com/docs/api/1.1/get/lists/list
query = twitter.lists.list(screen_name=username)
for i in query:
	print "-",i["name"],"list (id =",i["id"],") has",i["member_count"],"users."

# Choose a list
print ""
choice = raw_input("Enter the id of one of these lists: ")

# Load list members
cursor = -1
members = {}
print ""
print "Members of the list:"
while cursor != 0:
	try:
		# API: https://dev.twitter.com/docs/api/1.1/get/lists/members
		query = twitter.lists.members(list_id=choice, cursor=cursor)
		cursor = query["next_cursor"]
	except Exception,e:
		if "Rate limit exceeded" in str(e):
			print "Rate exceeded... waiting 15 minutes before retrying"
		
			# Countdown http://stackoverflow.com/questions/3249524/print-in-one-line-dynamically-python
			for k in range(1,60*15):
				remaining = 60*15 - k
				sys.stdout.write("\r%d seconds remaining   " % remaining)
				sys.stdout.flush()
				sleep(1)
			sys.stdout.write("\n")
			
			query = twitter.lists.members(list_id=choice, cursor=cursor)
			cursor = query["next_cursor"]
		
	for i in query["users"]:
		print "-",i["screen_name"],"(id =",i["id"],")"
		members[i["id"]] = i["screen_name"]

for i in members:
	# Load connections of each member
	print ""
	print "------------------------------------------------------------"
	print ""
	print "USER:",members[i]
	print ""
	print "Loading followers..."
	followers = load_connections([i], "followers")
	print ""
	print "Loading friends..."
	friends = load_connections([i], "friends")

	# Add edges...
	print ""
	print "Building the graph..."

	for f in followers:
		for k in followers[f]:
			graph.add_edge(k,f)
		
	for f in friends:
		for k in friends[f]:
			graph.add_edge(f,k)

# Prepare 100 ids lists for converting id to screen names
mapping = {}
lista = {}
position = 0
hundreds = 0
lista[hundreds] = []
for k in graph.nodes():
	if position == 100:
		hundreds += 1
		position = 0
		lista[hundreds] = []
	lista[hundreds].append(k)
	position += 1

# Convert id to screen names
print ""
print "Converting ids to screen names..."
for k in lista:
	try:
		# API: https://dev.twitter.com/docs/api/1.1/get/users/lookup
		query = twitter.users.lookup(user_id=lista[k])
	except Exception,e:
		if "Rate limit exceeded" in str(e):
			print "Rate exceeded... waiting 15 minutes before retrying"
		
			# Countdown http://stackoverflow.com/questions/3249524/print-in-one-line-dynamically-python
			for k in range(1,60*15):
				remaining = 60*15 - k
				sys.stdout.write("\r%d seconds remaining   " % remaining)
				sys.stdout.flush()
				sleep(1)
			sys.stdout.write("\n")
			
			query = twitter.users.lookup(user_id=lista[k])
	for i in query:
		mapping[i["id"]] = i["screen_name"]
		print i["id"],"=", i["screen_name"]

# Swap node names from ids to screen names
graph_screen_names = nx.relabel_nodes(graph,mapping)
	
# Save graph
print ""
print "The personal profile was analyzed succesfully.",errors,"errors were encountered.",len(graph_screen_names),"nodes in the network."
print ""
print "Saving the file as "+choice+"-twitter-list-network-1-degree.gexf..."
nx.write_gexf(graph_screen_names, choice+"-twitter-list-network-1-degree.gexf")