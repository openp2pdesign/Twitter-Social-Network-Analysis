# -*- encoding: utf-8 -*-
#
# Social Network Analysis of a Twitter user friendships
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
username = "fablaquila"
errors = 0
connections = {}

print ""
print "....................................................."
print "FRIENDSHIPS OF A TWITTER USER:",username
print ""	

def load_connections(user_list,option):
	for i in user_list:
		print ""
		if option == "followers":
			print "Loading users who follow",i,"..."
		else:
			print "Loading users who",i,"follows..."
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

# Load first degree of followers and friends
query = twitter.users.lookup(screen_name=username)
starting_user = []
starting_user.append(query[0]["id"])
first_followers = load_connections(starting_user, "followers")
first_friends = load_connections(starting_user, "friends")

second_followers_followers = load_connections(first_followers[starting_user[0]], "followers")
#second_followers_friends = load_connections(first_followers[starting_user[0]], "friends")
#second_friends_followers = load_connections(first_friends[starting_user[0]], "followers")
#second_friends_friends = load_connections(first_friends[starting_user[0]], "friends")

# Add edges...
print ""
print "Checking 2 degree connections..."

for f in first_followers:
	for k in first_followers[f]:
		graph.add_edge(k,f)
		
for f in first_friends:
	for k in first_friends[f]:
		graph.add_edge(f,k)

for f in second_followers_followers:
	for k in second_followers_followers[f]:
		graph.add_edge(k,f)

#for f in second_followers_friends:
#	for k in second_followers_friends[f]:
#		graph.add_edge(f,k)

#for f in second_friends_followers:
#	for k in second_friends_followers[f]:
#		graph.add_edge(k,f)

#for f in second_friends_friends:
#	for k in second_friends_friends[f]:
#		graph.add_edge(f,k)

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
print "The personal profile was analyzed succesfully.",errors,"errors were encountered."
print ""
print "Saving the file as "+username+"-twitter-personal-network-1.5-degree.gexf..."
nx.write_gexf(graph_screen_names, username+"-twitter-personal-network-1.5-degree.gexf")