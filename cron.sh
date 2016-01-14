#!/bin/sh

_cwd=`dirname $0`
cd $_cwd

date
. ./hnfeedcrawlerrc
./hnfeedcrawler.py

