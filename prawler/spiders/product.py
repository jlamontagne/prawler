import re
import json

from bs4 import BeautifulSoup
from prawler.items import Product
from prawler.utils.misc import text
from prawler.utils.pricing import get_prices
from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from urlparse import urljoin
from werkzeug.urls import url_fix

class ProductSpider(CrawlSpider):
    name = 'product'
    link_extractor = SgmlLinkExtractor()
    rules = [Rule(link_extractor, callback="parse_product")]

    def __init__(self, site, *a, **kw):
        super(ProductSpider, self).__init__(*a, **kw)

        with open(site) as fp:
            config = json.load(fp)

        if not 'domain' in config:
            raise Exception('No domain set for {}'.format(site))

        self.name = config['domain']
        self.allowed_domains = [self.name]
        self.start_urls = ['http://www.%s/' % self.name]

        if not 'selectors' in config:
            raise Exception('No CSS selectors defined for {}'.format(site))

        self.selectors = config['selectors']

    def parse_product(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        p = Product()

        for element, path in self.selectors.viewitems():
            node = soup.select_one(path)

            if not node:
                continue
            if element == 'image':
                p[element] = url_fix(urljoin(response.url, node['src']))
            else:
                p[element] = text(node)

        if 'name' in p and 'number' in p:
            p['url'] = response.url
            p['pricing'], p['discountcode'] = get_prices(soup)
            soup.decompose()
            yield p
        else:
            # Only follow links on non-product pages
            soup.decompose()
            for link in self.link_extractor.extract_links(response):
                yield Request(url=link.url)
