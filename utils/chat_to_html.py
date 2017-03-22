#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A variation of wall.py that specifically handles Twitter chats;
questions are expected to be in the form "Q1: What is your favorite
color?"
"""
from __future__ import print_function

import os
import re
import sys
import json
import requests
import fileinput
import argparse

AVATAR_DIR = "img"

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    outfile = os.path.join(AVATAR_DIR, local_filename)
    if not os.path.isfile(outfile):
        with open(outfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    return local_filename

parser = argparse.ArgumentParser()
parser.add_argument('--title', help='Title to put in chat summary', default='Your Title Here', type=str, required=True)
parser.add_argument('file', metavar='FILE', nargs=1, help='file to read')
args = parser.parse_args()

print("""<!doctype html>
<html>

<head>
  <meta charset="utf-8">
  <title>twarc wall</title>
  <style>
    body {
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12pt;
      margin-left: auto;
      margin-right: auto;
      width: 95%%;
    }

    section.tweet-group {
        clear: both;
    }

    article.tweet {
      position: relative;
      float: left;
      border: thin #eeeeee solid;
      margin: 10px;
      width: 270px;
      padding: 10px;
      height: 170px;
    }

    .name {
      font-weight: bold;
    }

    img.avatar {
        vertical-align: middle;
        float: inherit;
        margin-right: 10px;
        border-radius: 5px;
        height: 45px;
    }

    .tweet footer {
      position: absolute;
      bottom: 5px;
      left: 10px;
      font-size: smaller;
    }

    .tweet a {
      text-decoration: none;
    }

    footer#page {
      margin-top: 15px;
      clear: both;
      width: 100%%;
      text-align: center;
      font-size: 20pt;
      font-weight: heavy;
    }

    header {
      text-align: center;
      margin-bottom: 20px;
    }

  </style>
</head>

<body>

  <header>
  <h1>%(title)s</h1>
  </header>

  <div id="tweets">
  <section class="tweet-group">
""" % dict(title = args.title))

# Make avatar directory
if not os.path.isdir(AVATAR_DIR):
    os.makedirs(AVATAR_DIR)

lines = fileinput.input(files=args.file)

seen_questions = dict()
for line in lines:
    tweet = json.loads(line)

    # Download avatar
    url = tweet["user"]["profile_image_url"]
    filename = download_file(url)

    t = {
        "created_at": tweet["created_at"],
        "name": tweet["user"]["name"],
        "username": tweet["user"]["screen_name"],
        "user_url": "https://twitter.com/" + tweet["user"]["screen_name"],
        "text": tweet["text"],
        "avatar": AVATAR_DIR + "/" + filename,
        "url": "https://twitter.com/" + tweet["user"]["screen_name"] + "/status/" + tweet["id_str"],
    }

    if 'retweet_status' in tweet:
        t['retweet_count'] = tweet['retweet_status'].get('retweet_count', 0)
    else:
        t['retweet_count'] = tweet.get('retweet_count', 0)

    if t['retweet_count'] == 1:
        t['retweet_string'] = 'retweet'
    else:
        t['retweet_string'] = 'retweets'

    for url in tweet['entities']['urls']:
        a = '<a href="%(expanded_url)s">%(url)s</a>' % url
        start, end = url['indices']
        t['text'] = t['text'][0:start] + a + tweet['text'][end:]

    t['text'] = re.sub(' @([^ ]+)', ' <a href="https://twitter.com/\g<1>">@\g<1></a>', t['text'])
    t['text'] = re.sub(' #([^ ]+)', ' <a href="https://twitter.com/search?q=%23\g<1>&src=hash">#\g<1></a>', t['text'])
    m = re.match('^Q([0-9]+):', t['text']);
    if m:
        q = m.group(1);
        if not q in seen_questions:
            title = """
            </section>
            <section class="tweet-group">
            <h2>%(text)s</h2>
            """ % t
            print(title.encode('utf-8'))
            seen_questions[q] = True

    html = """
    <article class="tweet">
      <img class="avatar" src="%(avatar)s">
      <a href="%(user_url)s" class="name">%(name)s</a><br>
      <span class="username">%(username)s</span><br>
      <br>
      <span class="text">%(text)s</span><br>
      <footer>
      %(retweet_count)s %(retweet_string)s<br>
      <a href="%(url)s"><time>%(created_at)s</time></a>
      </footer>
    </article>
    """ % t

    print(html.encode("utf-8"))

print("""

</section>
</div>

<footer id="page">
<hr>
<br>
created on the command line with <a href="https://github.com/DocNow/twarc">twarc</a>.
<br>
<br>
</footer>

</body>
</html>""")
