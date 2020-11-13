import scrapy
import urllib.parse
import re
from datetime import datetime
from scrapy import Request
from dateutil import parser
import html2text

from demo.items import NewsItem


class BridgeRoadTopicsNewsSpider(scrapy.Spider):
    name = 'BridgeRoadTopicsNews'
    site_name = 'hkhktcd.vn'
    allowed_domains = ['hkhktcd.vn']

    page_template = '//div[@class="caca_page"]/a[text()="{}"]/@href'
    base_url = 'http://hkhktcd.vn/'

    start_urls = [
        'http://hkhktcd.vn/tap-chi-cau-duong/toan-canh-cau-duong-20,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/atgt-tkcn-29,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/doanh-nghiep-tai-chinh-36,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/trung-tam-dao-tao-37,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/chan-dung-khoa-hoc-38,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/o-to-xe-may-26,1.aspx',
        'http://hkhktcd.vn/tap-chi-cau-duong/tap-chi-cau-duong-viet-nam-18,1.aspx',
    ]

    def parse(self, response):
        posts = response.xpath('//*[@class="chuyenmuc_tintuc"]/div/div/a[1]/@href')
        if posts:
            for post in posts:
                url = post.extract()
                url = urllib.parse.urljoin(self.base_url, url)
                yield Request(url, callback=self.parse_post)

        url = response.url
        match = re.search(r'[0-9]{1,100},[0-9]{0,10}', url).group(0)
        # Get current page from url
        if match:
            current_page = match.split(',')[1]
            next_page = response.xpath(self.page_template.format(int(current_page) + 1)).get()
            if next_page:
                yield response.follow(next_page)

    def parse_post(self, response):
        """ This function returns newspaper articles on a given date in a given structure.

            Return data structure:
            [
                {
                            'title': string,                        # The title of a article
                            'author'                                # The author of a article, of '' if none
                            'subhead': string,                      # The subtitle of a article, or '' if there is no subtitle
                            'print': string,                        # The page number of a article
                            'date': string in '%Y-%m-%d' format,    # The publish date of a article
                            'timestamp': datetime                   # The ISO publish date of a article
                            'body': string                          # The body of a article
                            'pic': string in                        # The link of pictures of a article, or '' if there are no pictures
                                                                            f"{link1}|{text2}&&..." format
                            'link': string                          # The url of a article
                        },
                                ...
                    ]
                    or
                    None

                :param response: The scrapy response
                :return:
                """
        time_format, short_date, author = self.parse_date_author(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="noidung_chitiet"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="noidung_chitiet"]').get()),
            link=response.url,
            subhead='',
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date_author(self, response):
        """
        Convert time string to timestamp
        :param response:
        :return:
        """
        raw_time = html2text.html2text(response.xpath('//span[@class="timer"]').get())
        converted_time = parser.parse(raw_time.split('-')[0].strip().replace(' \\', ''))
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year), raw_time.split('-')[1]

    def parse_pictures(self, response):
        """
        Get pictures
        :param response:
        :return:
        """
        urls = response.xpath('//div[@class="noidung_chitiet"]//input[@type="image"]/@src').extract()
        if urls:
            urls = [urllib.parse.urljoin(self.base_url, item) for item in urls]
            captions = []
            count = 1
            for _ in urls:
                caption = response.xpath(
                    '//div[@class="noidung_chitiet"]//input[@type="image"][{}]/parent::*/following-sibling::*//em[1]/text()'.format(
                        count)).get()
                count += 1
            if caption:
                captions.append(caption)
            else:
                captions.append(' ')
            res = [i + '|' + j for i, j in zip(urls, captions)]
            result = '&&'.join(res)
            return result
        else:
            return ''
