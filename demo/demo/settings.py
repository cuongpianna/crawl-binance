BOT_NAME = 'demo'

SPIDER_MODULES = ['demo.spiders']
NEWSPIDER_MODULE = 'demo.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 1

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

ITEM_PIPELINES = {
    'demo.pipelines.MongoDBPipeline': 300,
}
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'

CONNECTION_STRING = 'sqlite:///news.db'

# USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"


MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "TestWelders"
MONGODB_COLLECTION = "product"
MONGODB_COLLECTION_CATE = "category"
