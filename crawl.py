#!/usr/bin/env python
import argparse

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings
from prawler.spiders.product import ProductSpider
from os import path, walk

settings = get_project_settings()

parser = argparse.ArgumentParser(description='Import product information.')
parser.add_argument('sites_dir')
args = parser.parse_args()

(_, _, sites) = next(walk(args.sites_dir))

for site in sites:
    spider = ProductSpider(path.join(args.sites_dir, site))
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()

log.start(loglevel='DEBUG')
reactor.run()
