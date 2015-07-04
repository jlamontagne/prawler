BOT_NAME = 'prawler'
LOG_LEVEL = 'DEBUG'

SPIDER_MODULES = ['prawler.spiders']
NEWSPIDER_MODULE = 'prawler.spiders'

# ITEM_PIPELINES = {'prawler.pipelines.ProductPipeline': 1}

IMAGES_MIN_WIDTH = 50
IMAGES_MAX_WIDTH = 50
IMAGES_STORE = '/home/josh/src/prawler-import/trakker-images'
IMAGES_EXPIRES = 90
IMAGES_THUMBS = {
    'small': (139, 139)
}

COOKIES_ENABLED = True
DEPTH_LIMIT = 5
DOWNLOAD_DELAY = 4
DOWNLOAD_TIMEOUT = 30
METAREFRESH_MAXDELAY = 5
REDIRECT_MAX_TIMES = 1
RETRY_ENABLED = False
ROBOTSTXT_OBEY = True

FEED_EXPORTERS = {
    'pprint': 'scrapy.contrib.exporter.PprintItemExporter'
}

FEED_FORMAT = 'jsonlines'
FEED_URI = 'file:///home/josh/src/prawler-import/feeds/%(name)s/%(time)s.json'

DOWNLOAD_HANDLERS = {
    'phantomjs-http': 'prawler.downloader.handlers.phantomjs.PhantomJSDownloadHandler'
  , 'phantomjs-https': 'prawler.downloader.handlers.phantomjs.PhantomJSDownloadHandler'
}

SPIDER_MIDDLEWARES = {
    'prawler.spidermiddleware.phantomjs.PhantomJSMiddleware': 10
}

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = '/home/josh/src/prawler-import/cache'
HTTPCACHE_EXPIRATION_SECS = 2592000 # 30 days
HTTPCACHE_POLICY = 'scrapy.contrib.httpcache.DummyPolicy'
