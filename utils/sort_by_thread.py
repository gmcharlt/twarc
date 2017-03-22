#!/usr/bin/env python
"""
Sort tweets by ID and thread.

Sorts a collection of tweets into threaded order, e.g.

- tweet 1
  - reply to tweet 1
  - another reply to tweet 1
  - a tweet quoting tweet 1
- tweet 2
- tweet 3
  - reply to tweet 3

etc.

Based on utils/sort_by_id.py.

Example usage:
utils/sort_by_thread.py tweets.json > sorted.json
"""
from __future__ import print_function

import json
from operator import itemgetter
import fileinput
from collections import defaultdict


tweets = dict()
parents = dict()
desc = defaultdict(list)
for line in fileinput.input():
    tweet = json.loads(line)
    id = str(tweet['id'])
    parent_id = None
    if 'in_reply_to_status_id_str' in tweet:
        parent_id = tweet['in_reply_to_status_id_str']
    elif 'quoted_status' in tweet:
        parent_id = tweet['quoted_status']
    parents[id] = parent_id
    if parent_id is not None:
        desc[parent_id].append(id)
    tweets[id] = tweet

roots = [tweets[x] for x in tweets.keys() if parents[x] is None or parents[x] not in tweets]
roots = sorted(roots, key=itemgetter('id'))

def print_children(id, level = 1):
    global tweets
    global desc
    children = [tweets[x] for x in desc[id]]
    children = sorted(children, key=itemgetter('id'))
    for tweet in children:
        print(json.dumps(tweet))
        print_children(str(tweet['id']), level = level + 1)

for tweet in roots:
    print(json.dumps(tweet))
    print_children(str(tweet['id']))

# End of file
