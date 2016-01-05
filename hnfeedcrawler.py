#!/usr/bin/env python2.6

import feedparser
import hashlib
import json
import os
import psycopg2
import sys
import time
from datetime import datetime

#print feed

class HackerNewsCrawler:
    url = 'https://news.ycombinator.com/rss'
    feed = None
    dbname = None
    dbuser = None
    conn = None
    md5 = None

    def __init__(self):
        if 'DBNAME' in os.environ:
            self.dbname = os.environ["DBNAME"]
        if 'DBUSER' in os.environ:
            self.dbuser = os.environ["DBUSER"]

        if self.dbname is None or self.dbuser is None:
            print("DBNAME and DBUSER must be specified.")
            sys.exit(1)

    def start(self):
        self.connectdb()

    def connectdb(self):
        connstr = "dbname=%s user=%s" % (self.dbname, self.dbuser)
        print(connstr)
        self.conn = psycopg2.connect(connstr)

    def parse(self):
        self.feed = feedparser.parse(self.url)

    def default_conv(self,v):
        if isinstance(v, time.struct_time):
            return datetime(*v[:6]).isoformat()
        raise TypeError(repr(v) + " is not JSON serializable")

    def run(self, verbose=False):
        self.parse()

        cur = self.conn.cursor()

        for e in self.feed.entries:
            published = datetime(*e['published_parsed'][:6]).isoformat()
            title = e['title']
            link = e['link']
            link_digest = hashlib.md5(e['link']).hexdigest()
            comments = e['comments']
            comments_digest = hashlib.md5(e['comments']).hexdigest()
            feed = json.dumps(e, default=self.default_conv)

            if verbose is True:
                print published
                print title
                print link
                print link_digest
                print comments
                print comments_digest
                print feed
                print ""

            cur.execute("SELECT itemid FROM hn_feed WHERE link_digest = %s", [link_digest])
            item = cur.fetchone()
            if item is not None:
                print ("link_digest '%s' already exists. (seq = %d)" % (link_digest, item[0]))
            else:
                cur.execute("INSERT INTO hn_feed (published,title,link,comments,link_digest,comments_digest,feed) VALUES (%s,%s,%s,%s,%s,%s,%s)", (published,title,link,comments,link_digest,comments_digest,feed))
                print ("link_digest '%s' appneded." % (link_digest))

        self.conn.commit()
        cur.close()

    def finish(self):
        self.conn.close()

crawler = HackerNewsCrawler()

crawler.start()
crawler.run()
crawler.finish()

sys.exit(0)
