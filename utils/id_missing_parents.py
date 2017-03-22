#!/usr/bin/env python
"""
Get IDs of parent tweets not already present in file.

Example usage:
utils/id_missing_parents.py tweets.json > parent_ids.txt
"""
from __future__ import print_function

import json
import fileinput

tweets = dict()
parents = dict()
for line in fileinput.input():
    tweet = json.loads(line)
    id = str(tweet['id'])

    if 'in_reply_to_status_id_str' in tweet:
        parents[id] = tweet['in_reply_to_status_id_str']
    elif 'quoted_status' in tweet:
        parents[id] = tweet['quoted_status']

    tweets[id] = True

missing_parents = [x for x in tweets.keys() if parents[x] is not None and parents[x] not in tweets]

for parent in missing_parents:
    print(parent)
