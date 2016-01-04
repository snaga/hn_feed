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
    dbuser = "p_nagayasu_satoshi"

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

    def run(self):
        self.parse()

        for e in self.feed.entries:
#    print type(e)
            print datetime(*e['published_parsed'][:6]).isoformat()
            print e['title']
            print e['link']
            print md5.new(e['link']).hexdigest()
            print e['comments']
            print md5.new(e['comments']).hexdigest()
            print json.dumps(e, default=self.default_conv)
            print ""

    def finish(self):
        self.conn.close()

crawler = HackerNewsCrawler()

crawler.connectdb()
crawler.run()
crawler.finish()
