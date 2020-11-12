import scrapy
from scrapy import Request
import html2text
import dateutil.parser

from demo.items import NewsItem


class HeritageSpider(scrapy.Spider):
    name = 'Heritage'
    site_name = 'heritagevietnamairlines.com'
    allowed_domains = ['heritagevietnamairlines.com']
    start_urls = ['http://heritagevietnamairlines.com/category/tin-tuc/',
                  'http://heritagevietnamairlines.com/category/du-lich-diem-den/',
                  'http://heritagevietnamairlines.com/category/du-lich-diem-den/quoc-noi/',
                  'http://heritagevietnamairlines.com/category/du-lich-diem-den/quoc-te/',
                  'http://heritagevietnamairlines.com/category/di-san-van-hoa/',
                  'http://heritagevietnamairlines.com/category/di-san-van-hoa/nghe-thuat/',
                  'http://heritagevietnamairlines.com/category/di-san-van-hoa/van-hoa-dia-phuong/',
                  'http://heritagevietnamairlines.com/category/di-san-van-hoa/chuyen-co-tich/',
                  'http://heritagevietnamairlines.com/category/di-san-van-hoa/lich-cac-le-hoi/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/su-kien/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/bst-thoi-trang/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/thuong-hieu/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/phong-cach-song/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/song-xanh/',
                  'http://heritagevietnamairlines.com/category/cuoc-song-duong-dai/kinh-doanh/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/the-le-giai/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/tin-tuc-giai/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/hang-muc-anh-bo/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/hang-muc-anh-bia/',
                  'http://heritagevietnamairlines.com/category/giai-thuong-heritage/hang-muc-anh-don/'
                  ]

    def parse(self, response):
        top_news = response.xpath('//h3[@class="h3-title large-box__title"]/a').css('::attr(href)')
        for post in top_news:
            url_extract = post.extract()
            yield Request(url_extract, callback=self.parse_post)

        three_news = response.xpath('//h3[@class="box__title h3-title"]/a').css('::attr(href)')
        if three_news:
            for post in three_news:
                url_extract = post.extract()
                yield Request(url_extract, callback=self.parse_post)

        posts = response.xpath('//h3[@class="t-h3"]/a').css('::attr(href)')

        if posts:
            for post in posts:
                url_extract = post.extract()
                yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//li[@class="pagination__item next"]/a')

        if next_page:
            next_url = response.xpath('//li[@class="pagination__item next"]/a').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h2[@class="post-title"]/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="elementor-widget-wrap"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="elementor-widget-wrap"]').get()),
            link=response.url,
            subhead='',
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        """
        Convert datetime string to timestamp, date
        :param response: 2019-11-20T16:23:59+00:00
        :return:
        """
        created_raw = response.xpath('//meta[@property="article:published_time"]/@content').get()
        converted_time = dateutil.parser.isoparse(created_raw)

        short_date = '{}/{}/{}'.format(converted_time.month, converted_time.day, converted_time.year)
        time_format = converted_time.isoformat()
        return time_format, short_date

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//div[@class="bzc-image-wrapper"]/img/@src').extract()
        captions = response.xpath('//div[@class="elementor-image"]//figcaption/text()').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    def parse_author(self, response):
        if response.xpath('//div[@class="elementor-widget-wrap"]/div[1]//span/text()').get():
            author = response.xpath('//div[@class="elementor-widget-wrap"]/div[1]//span/text()').get()
        else:
            author = ''
        return author
