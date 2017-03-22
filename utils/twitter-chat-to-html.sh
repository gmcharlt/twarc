#!/bin/bash

# Given a tweet JSON file from a Twitter chat, produce
# an HTML version.
#
# Usage:
#
# twitter-chat-to-html.sh TWEETS OUTPUT_HTML TITLE SINCE_TIME
#
# e.g.,
#
# twitter-chat-to-html.sh tweets.json chat.html "Twitter chat" "2017-01-01 12:00"

set -e

SRC=$1
DEST=$2
TITLE=$3
START=$4

export PATH=.:$PATH

tmpdir=$(mktemp -d)

# filter out retweets
noretweets.py $SRC > $tmpdir/step1

# start at the beginning of the chat
filter_date.py --mindate "$START" $tmpdir/step1 > $tmpdir/step2

# find missing parents (often cases where a chat
# participate forgot to use the hashtag but somebody
# responded to them anyway on the hashtag)
id_missing_parents.py $tmpdir/step2 > $tmpdir/parents.txt
twarc.py --hydrate $tmpdir/parents.txt > $tmpdir/parents.json
cat $tmpdir/parents.json $tmpdir/step2 > $tmpdir/step3

# 
sort_by_thread.py $tmpdir/step3 > $tmpdir/step4

chat_to_html.py --title "$TITLE" $tmpdir/step4 > $DEST

rm -Rf tmpdir
