# -*- encoding: utf-8 -*-
#
# Social Network Analysis of a Twitter hashtag search
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
import json
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.DiGraph()

print ""
print "....................................................."
print "RT NETWORK OF AN HASHTAG"
print ""	

hashtag = "#opendesign"

# Log in
OAUTH_TOKEN = "Insert here"
OAUTH_SECRET = "Insert here"
CONSUMER_KEY = "Insert here"
CONSUMER_SECRET = "Insert here"

auth = OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter = Twitter(auth = auth)

# search
# https://dev.twitter.com/docs/api/1.1/get/search/tweets
query = twitter.search.tweets(q=hashtag, count=100)

# Debug line
#print json.dumps(query, sort_keys=True, indent=4)

# Print results
print "Search complete (%f seconds)" % (query["search_metadata"]["completed_in"])
print "Found",len(query["statuses"]),"results."

# Get results and find retweets and mentions
for result in query["statuses"]:
	print ""
	print "Tweet:",result["text"]
	print "By user:",result["user"]["name"]
	if len(result["entities"]["user_mentions"]) != 0:
		print "Mentions:"
		for i in result["entities"]["user_mentions"]:
			print " - by",i["screen_name"]
			graph.add_edge(i["screen_name"],result["user"]["name"])
	if "retweeted_status" in result:
		if len(result["retweeted_status"]["entities"]["user_mentions"]) != 0:
			print "Retweets:"
			for i in result["retweeted_status"]["entities"]["user_mentions"]:
				print " - by",i["screen_name"]
				graph.add_edge(i["screen_name"],result["user"]["name"])
	else:
		pass
	
# Save graph
print ""
print "The network of RT of the hashtag was analyzed succesfully."
print ""
print "Saving the file as "+hashtag+"-rt-network.gexf..."
nx.write_gexf(graph, hashtag+"-rt-network.gexf")