# start 2h
import scrapy
from datetime import datetime
import json
from scrapy import Request, FormRequest
import html2text
from dateutil import parser

from demo.items import NewsItem

categories = {

}


class VietnamBanksAssociationSpider(scrapy.Spider):
    name = 'VietnamBanksAssociation'
    site_name = 'thitruongtaichinhtiente.vn'
    allowed_domains = ['thitruongtaichinhtiente.vn']
    base_url = 'https://thitruongtaichinhtiente.vn/'

    api = 'https://thitruongtaichinhtiente.vn/api/getMoreArticle'

    start_urls = ['https://thitruongtaichinhtiente.vn/su-kien',
                  'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang',
                  'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te',
                  'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu',
                  'https://thitruongtaichinhtiente.vn/nhin-ra-the-gioi',
                  'https://thitruongtaichinhtiente.vn/cong-nghe',
                  'https://thitruongtaichinhtiente.vn/ket-noi',
                  'https://thitruongtaichinhtiente.vn/van-hoa',
                  'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te'
                  ]

    def parse(self, response):
        next_page = response.xpath('//div[@class="itemBox loadArticle"][12]/@pid')

        if next_page:
            top_news = response.xpath('//div[@class="newsTop"]//h3/a').css('::attr(href)')
            right_news = response.xpath('//div[@class="newsTop"]//h2/a').css('::attr(href)')
            follow_news = response.xpath('div[@class="newsDS"]//div[@class="info"]/a').css('::attr(href)')
            self.yield_post(top_news)
            self.yield_post(right_news)
            self.yield_post(follow_news)

            form_data = {"type": "channel", "channelId": str(self.get_cate_id(response.url)),
                         "publisherId": str(next_page.get())}

            yield FormRequest(self.api, formdata=form_data, callback=self.parse)
        else:
            body = json.loads(response.body)
            for item in body:
                yield Request(item['LinktoMe'], callback=self.parse_post)

            last_item = body[-1]
            publish_id = str(last_item['PublisherId'])
            channel_id = str(last_item['Channel']['ParentId'])
            form_data = {"type": "channel", "channelId": channel_id,
                         "publisherId": publish_id}
            yield FormRequest(self.api, formdata=form_data, callback=self.parse)

    def yield_post(self, posts):
        if posts:
            for news in posts:
                url = news.extract()
                yield Request(url, callback=self.parse_post)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="description"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="description"]').get()),
            link=response.url,
            subhead=response.xpath('//div[@class="shortDesc"]/text()').get().strip(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        """
        Convert string to timestamp
        :param response: - 03/09/2020 10:33
        :return: timestamp, date
        """

        raw_time = response.xpath('//div[@class="infoTime"]/text()').extract()[1].strip()[2:]
        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour, day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day, converted_time.year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//*[@class="imageBox"]//img/@src').extract()
        captions = response.xpath('//*[@class="imageBox"]//p[@class="PCaption"]/text()').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    def get_cate_id(self, link):
        if link == 'https://thitruongtaichinhtiente.vn/su-kien':
            return 5
        elif link == 'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang':
            return 156
        elif link == 'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te':
            return 195
        elif link == 'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu':
            return 160
        elif link == 'https://thitruongtaichinhtiente.vn/nhin-ra-the-gioi':
            return 186
        elif link == 'https://thitruongtaichinhtiente.vn/cong-nghe':
            return 202
        elif link == 'https://thitruongtaichinhtiente.vn/ket-noi':
            return 199
        elif link == 'hhttps://thitruongtaichinhtiente.vn/van-hoa':
            return 168

    @staticmethod
    def parse_author(response):
        if response.xpath('//div[@class="infoTime"]/span[1]/text()').get():
            return response.xpath('//div[@class="infoTime"]/span[1]/text()').get().replace('- ', '').strip()
        else:
            return ''
