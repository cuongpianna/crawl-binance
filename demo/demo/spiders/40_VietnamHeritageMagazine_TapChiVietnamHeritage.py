# 1h
import scrapy
from scrapy import Request
import html2text
import dateutil.parser


from demo.items import NewsItem


class VietnamHeritageMagazineSpider(scrapy.Spider):
    name = 'VietnamHeritageMagazine'
    site_name = 'vietnamheritage.com.vn'
    allowed_domains = ['vietnamheritage.com.vn']
    start_urls = ['http://www.vietnamheritage.com.vn/category/travel/',
                  'http://www.vietnamheritage.com.vn/category/whats-on/',
                  'http://www.vietnamheritage.com.vn/category/arts-and-culture/history/',
                  'http://www.vietnamheritage.com.vn/category/food/',
                  'http://www.vietnamheritage.com.vn/category/photography/',
                  'http://www.vietnamheritage.com.vn/category/arts-and-culture/']

    def parse(self, response):
        posts = response.xpath('//article//h2/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@class="next page-numbers"]')

        if next_page:
            next_url = response.xpath('//a[@class="next page-numbers"]').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//section[@class="cb-entry-content clearfix"]').get(),
            body=html2text.html2text(response.xpath('//section[@class="cb-entry-content clearfix"]').get()),
            link=response.url,
            subhead='',
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        # 2019-11-20T16:23:59+00:00
        created_raw = response.xpath('//meta[@itemprop="datePublished"]/@content').get()
        converted_time = dateutil.parser.isoparse(created_raw)

        short_date = '{}/{}/{}'.format(converted_time.month, converted_time.day, converted_time.year)
        time_format = converted_time.isoformat()
        return time_format, short_date

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//section[@class="cb-entry-content clearfix"]//img/@src').extract()
        if urls:
            result = '&&'.join(urls)
            return result
        else:
            return ''

    def parse_author(self, response):
        if response.xpath('//p[@style="text-align: right;"]/strong/text()').extract():
            author = response.xpath('//p[@style="text-align: right;"]/strong/text()')[-1].extract()
        elif response.xpath('//p[@style="text-align: right;"]/span/text()'):
            author = response.xpath('//p[@style="text-align: right;"]/span/text()')[-1].extract()
        elif response.xpath('//div[@id="author"]/span/text()'):
            author = response.xpath('//div[@id="author"]/span/text()').get()
        else:
            author = ''
        return author
