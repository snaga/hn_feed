#!/usr/bin/env python2.7

import feedparser
import md5
import time
from datetime import datetime
import json
import psycopg2

#print feed

class HackerNewsCrawler:
    url = 'https://news.ycombinator.com/rss'
    feed = None
    dbname = "hnfeed"
    dbuser = "snaga"
    conn = None

    def __init__(self):
        pass

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
            link_digest = md5.new(e['link']).hexdigest()
            comments = e['comments']
            comments_digest = md5.new(e['comments']).hexdigest()
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

crawler.connectdb()
crawler.run()
crawler.finish()
