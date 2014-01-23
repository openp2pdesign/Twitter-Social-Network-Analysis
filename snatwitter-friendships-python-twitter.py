# -*- encoding: utf-8 -*-
#
# Social Network Analysis of a Twitter user friendships
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: GPL v.3
#
# Requisite: 
# install python-twitter with pip install python-twitter
# install NetworkX with pip install networkx
#
# python-twitter documentation: http://static.unto.net/python-twitter/0.6/doc/twitter.html
#
# Other Twitter libraries: https://dev.twitter.com/docs/twitter-libraries
#

import twitter
import networkx as nx
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.DiGraph()

print ""
print "....................................................."
print "FRIENDSHIPS OF A TWITTER USER"
print ""	

username = "openp2pdesign"

# Get them from http://dev.twitter.com
OAUTH_TOKEN = "Insert here"
OAUTH_SECRET = "Insert here"
CONSUMER_KEY = "Insert here"
CONSUMER_SECRET = "Insert here"

# Log in
api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=OAUTH_TOKEN,
                      access_token_secret=OAUTH_SECRET)

# Load data
print "Loading users who follow",username,"..."
followers = []
followers.extend(api.GetFollowers(screen_name=username))

print "Loading users that",username,"follows..."
friends = []
friends.extend(api.GetFriends(screen_name=username))

# Create graph
print "Adding followers relationships..."
for user in followers:
	graph.add_edge(user.name,username)
	
print "Adding following relationships..."
for user in friends:
	graph.add_edge(username,user.name)
	
# Save graph
print ""
print "The personal profile was analyzed succesfully."
print ""
print "Saving the file as "+username+"-personal-network.gexf..."
nx.write_gexf(graph, username+"-personal-network.gexf")