BOT_NAME = 'demo'

SPIDER_MODULES = ['demo.spiders']
NEWSPIDER_MODULE = 'demo.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 1


DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

FEED_EXPORT_FIELDS = ['date', 'timestamp', 'title', 'subhead', 'author', 'link', 'pic', 'body', 'content_html']
#USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
