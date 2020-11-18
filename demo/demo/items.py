import scrapy


class NewsItem(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    content_html = scrapy.Field()
    timestamp = scrapy.Field()
    print = scrapy.Field()
    original_link = scrapy.Field()
    subhead = scrapy.Field()
    pic_list = scrapy.Field()
    date = scrapy.Field()
    source = scrapy.Field()