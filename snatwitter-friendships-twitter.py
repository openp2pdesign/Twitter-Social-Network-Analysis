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
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.DiGraph()

print ""
print "....................................................."
print "FRIENDSHIPS OF A TWITTER USER"
print ""	

username = "rasmusvuori"

errors = 0

# Get them from http://dev.twitter.com
OAUTH_TOKEN = "Insert here"
OAUTH_SECRET = "Insert here"
CONSUMER_KEY = "Insert here"
CONSUMER_SECRET = "Insert here"

# Log in
auth = OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter = Twitter(auth = auth)

# Load first degree of followers and friends
print ""
print "Loading users who follow",username,"..."
followers_query = {}
counting = 0
cursor = -1
followers = {}

while cursor != "0":
	followers_query = twitter.followers.list(screen_name=username,count=200,cursor=cursor)
	cursor = followers_query["next_cursor_str"]
	for id in followers_query["users"]:
		followers[id["id"]] = id["screen_name"]
		print " - ",id["screen_name"],"id =",id["id"]

print ""
print "Loading users that",username,"follows..."
friends_query = {}
counting = 0
cursor = -1
friends = {}

while cursor != "0":
	friends_query = twitter.friends.list(screen_name=username,count=200,cursor=cursor)
	cursor = friends_query["next_cursor_str"]
	for id in friends_query["users"]:
		friends[id["id"]] = id["screen_name"]
		print " - ",id["screen_name"],"id =",id["id"]

# Create graph
print ""
print "Adding followers relationships..."
for id in followers:
	graph.add_edge(followers[id],username)

print ""
print "Adding following relationships..."
for id in friends:
	graph.add_edge(username,friends[id])

## here new part

followers_total = {}

# Load first degree of followers and friends for each user
for i in followers:
	print ""
	print "Loading users who follow",followers[i],"..."
	followers_query = {}
	counting = 0
	cursor = -1
	followers_total[followers[i]] = {}

	while cursor != "0":
		try:
			followers_query = twitter.followers.list(screen_name=followers[i],count=200,cursor=cursor)
			cursor = followers_query["next_cursor_str"]
			for id in followers_query["users"]:
				followers_total[followers[i]][id["id"]] = id["screen_name"]
				print " - ",id["screen_name"],"id =",id["id"]
		except Exception,e:
			print "Error:",e
			print "There were some errors with user",followers[i],"; most likely it is a protected user"
			cursor = "0"

print "test"
exit()
## here new part

	
# Save graph
print ""
print "The personal profile was analyzed succesfully.",errors,"errors were encountered."
print ""
print "Saving the file as "+username+"-personal-network.gexf..."
nx.write_gexf(graph, username+"-personal-network.gexf")