#!/usr/bin/env python2.6

import feedparser
import hashlib
import html2text
import json
import lxml
import os
import psycopg2
import sys
import time
import urllib
from datetime import datetime
from readability.readability import Document

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
                content = self.get_page_content(link)

                cur.execute("INSERT INTO hn_feed (published,title,link,comments,link_digest,comments_digest,feed,content) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (published,title,link,comments,link_digest,comments_digest,feed,content))
                print ("link_digest '%s' appneded." % (link_digest))

        self.conn.commit()
        cur.close()

    def get_page_content(self, url):
        try:
            u = urllib.urlopen(url)

            if 'Content-Type' not in u.info():
                return None
            ctype = u.info()['Content-Type']
            if ctype.startswith("text/") is False:
                print("The content is not text. (%s)" % ctype)
                return None

            html = u.read()
            title = Document(html).short_title()

            h2t = html2text.HTML2Text()
            h2t.ignore_links = True
            h2t.ignore_images = True
            article = h2t.handle(Document(html).summary())

        except lxml.etree.XMLSyntaxError, err:
            return None
        except IOError, err:
            return None

        return title + "\n\n" + article

    def finish(self):
        self.conn.close()

crawler = HackerNewsCrawler()

crawler.start()
crawler.run()
crawler.finish()

sys.exit(0)
