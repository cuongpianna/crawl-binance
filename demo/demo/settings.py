BOT_NAME = 'demo'

SPIDER_MODULES = ['demo.spiders']
NEWSPIDER_MODULE = 'demo.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 1


DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

ITEM_PIPELINES = {
   'demo.pipelines.SaveNewsPipeline': 300,
}

CONNECTION_STRING = 'sqlite:///news.db'

FEED_EXPORT_FIELDS = ['date', 'timestamp', 'title', 'subhead', 'author']
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
