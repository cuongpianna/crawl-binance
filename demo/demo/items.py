import scrapy


class NewsItem(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    content_html = scrapy.Field()
    timestamp = scrapy.Field()
    tags = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    subhead = scrapy.Field()
    pic = scrapy.Field()
    date = scrapy.Field()