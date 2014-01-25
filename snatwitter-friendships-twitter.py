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
username = "openmetadesign"
errors = 0

print ""
print "....................................................."
print "FRIENDSHIPS OF A TWITTER USER:",username
print ""	

def load_connections(user_list,option):
	connections = {}
	for i in user_list:
		print ""
		if option == "followers":
			print "Loading users who follow",user_list[i],"..."
		else:
			print "Loading users who",user_list[i],"follows..."
		query = {}
		counting = 0
		cursor = -1
		connections[user_list[i]] = {}

		while cursor != "0":
			try:
				if option == "followers":
					query = twitter.followers.list(screen_name=user_list[i],count=200,cursor=cursor)
				else:
					query = twitter.friends.list(screen_name=user_list[i],count=200,cursor=cursor)
				cursor = query["next_cursor_str"]
				for id in query["users"]:
					connections[user_list[i]][id["id"]] = id["screen_name"]
					print " - ",id["screen_name"],"id =",id["id"]
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
						query = twitter.followers.list(screen_name=user_list[i],count=200,cursor=cursor)
					else:
						query = twitter.friends.list(screen_name=user_list[i],count=200,cursor=cursor)
					cursor = query["next_cursor_str"]
					for id in query["users"]:
						connections[user_list[i]][id["id"]] = id["screen_name"]
						print " - ",id["screen_name"],"id =",id["id"]
				elif "Not authorized" in str(e):				
					print "There were some errors with user",user_list[i],"... most likely it is a protected user"
					cursor = "0"
				else:
					print "Some error happened with user",user_list[i]
					cursor = "0"
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
starting_user = {query[0]["id"]: username}
first_followers = load_connections(starting_user, "followers")
first_friends = load_connections(starting_user, "friends")

# Load second degree of followers and friends
second_followers_followers = {}
second_followers_friends = {}
second_friends_followers = {}
second_friends_friends = {}

for id in first_followers:
	second_followers_followers[id] = load_connections(first_followers[id], "followers")
for id in first_followers:
	second_followers_friends[id] = load_connections(first_followers[id], "friends")
for id in first_friends:
	second_friends_followers[id] = load_connections(first_friends[id], "followers")
for id in first_friends:
	second_friends_friends[id] = load_connections(first_friends[id], "friends")

# Create graph
print ""
print "Followers: adding followers relationships..."
for i in second_followers_followers[username]:
	graph.add_edge(i,username)
	for k in second_followers_followers[username][i]:
		graph.add_edge(second_followers_followers[username][i][k],i)

print ""
print "Followers: adding friends relationships..."
for i in second_followers_friends[username]:
	for k in second_followers_followers[username][i]:
		graph.add_edge(i,second_followers_followers[username][i][k])

print ""
print "Friends: adding followers relationships..."
for i in second_friends_followers[username]:
	graph.add_edge(username,i)
	for k in second_friends_followers[username][i]:
		graph.add_edge(second_friends_followers[username][i][k],i)

print ""
print "Friends: adding friends relationships..."
for i in second_friends_friends[username]:
	for k in second_friends_friends[username][i]:
		graph.add_edge(i,second_friends_friends[username][i][k])

	
# Save graph
print ""
print "The personal profile was analyzed succesfully.",errors,"errors were encountered."
print ""
print "Saving the file as "+username+"-twitter-personal-network.gexf..."
nx.write_gexf(graph, username+"-twitter-personal-network.gexf")