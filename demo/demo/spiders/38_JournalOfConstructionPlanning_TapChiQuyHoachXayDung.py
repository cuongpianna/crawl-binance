# 1 hour
import scrapy
from datetime import datetime
from dateutil import parser
import html2text
from demo.items import NewsItem
import urllib.parse


class JournalOfConstructionPlanningSpider(scrapy.Spider):
    name = 'JournalOfConstructionPlanning'
    site_name = 'www.viup.vn'
    base_url = 'https://www.viup.vn/'
    allowed_domains = ['www.viup.vn']

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    start_urls = ['https://www.viup.vn/vn/Tin-tong-hop-n3.html', 'https://www.viup.vn/vn/Tin-quoc-te-n18.html',
                  'https://www.viup.vn/vn/Tin-VIUP-n2.html',
                  'https://www.viup.vn/vn/Van-de-nong-n106.html',
                  'https://www.viup.vn/vn/Quy-chuan-tieu-chuan-trong-QHXD-n112.html',
                  'https://www.viup.vn/vn/Luat-QH-va-tac-dong-cua-luat-QH-doi-voi-Quy-hoach-DT-va-NT-n111.html',
                  'https://www.viup.vn/vn/Quy-hoach-he-thong-DT-va-NT-n110.html',
                  'https://www.viup.vn/vn/Do-thi-nen-n118.html'
                  ]

    def parse(self, response):
        col_left = response.xpath('//section[@class="inner-site"]/div[@class="col-sm-3"]').get()
        if col_left:
            posts = response.xpath('//a[@class="img-qh"]').css('::attr(href)')
            if posts:
                for post in posts:
                    url_extract = post.extract()
                    yield response.follow(url_extract, callback=self.parse_post)
        else:
            posts = response.xpath('//div[@class="nd-new"]/a').css('::attr(href)')
            if posts:
                for post in posts:
                    url_extract = post.extract()
                    print(url_extract)
                    yield response.follow(url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@title="Next page"]/@href')

        if next_page:
            yield response.follow(next_page.get())

    def parse_post(self, response):
        author = self.parse_author(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get().strip(),
            timestamp='',
            content_html=response.xpath('//div[@class="content_detail"]').get(),
            body=self.parse_body(response),
            link=response.url,
            subhead=response.xpath('//div[@class="teaser_detail"]/text()').get() if response.xpath(
                '//div[@class="teaser_detail"]/text()').get() else '',
            pic=self.parse_pictures(response),
            date='',
            author=author
        )
        yield item

    def parse_body(self, response):
        return html2text.html2text(response.xpath('//div[@class="content_detail"]').get())

    def parse_date(self, response):
        """
        Convert string to timestamp
        :param response: - Time format:  08-11-2020 15:11
        :return: timestamp, date
        """
        raw_time = response.xpath("//div[contains(@class, 'time_detail_news')]/text()").get()

        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    def parse_pictures(self, response):
        """
        Get list pictures with their caption
        :param response:
        :return:
        """
        urls = response.xpath('//div[@class="content_detail"]/p/img/@src').extract()
        urls = [urllib.parse.urljoin(self.base_url, item) for item in urls]
        template = '(//div[@class="content_detail"]//img)[{}]/parent::p/following-sibling::p[1]//em/text()'
        count = 1
        captions = []
        for _ in urls:
            caption = response.xpath(template.format(count)).get()
            if caption:
                captions.append(caption)
            else:
                captions.append('')
            count += 1

        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        """
        Get news author
        :param response:
        :return:
        """
        if response.xpath('//div[@class="new-source"]/text()').get():
            return response.xpath('//div[@class="new-source"]/text()').get()
        else:
            return ''
