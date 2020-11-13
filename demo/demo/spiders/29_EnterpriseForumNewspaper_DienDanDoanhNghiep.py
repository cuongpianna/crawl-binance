import scrapy
from datetime import datetime
from urllib.parse import urljoin
from scrapy_selenium import SeleniumRequest
from dateutil import parser
import time

from demo.items import NewsItem


class EnterpriseForumNewspaper(scrapy.Spider):
    name = 'EnterpriseForumNewspaper'
    site_name = 'enternews.vn'
    allowed_domains = ['enternews.vn']
    start_urls = ['https://enternews.vn/thoi-su-c82', 'https://enternews.vn/cai-cach-hanh-chinh-c204',
                  'https://enternews.vn/van-de-hom-nay-c239', 'https://enternews.vn/van-hoa-xa-hoi-c240',
                  'https://enternews.vn/chinh-tri-c241', 'https://enternews.vn/doanh-nhan-c22',
                  'https://enternews.vn/suc-khoe-c326', 'https://enternews.vn/nhan-vat-c212',
                  'https://enternews.vn/cafe-doanh-nhan-c324', 'https://enternews.vn/phong-cach-song-c325',
                  'https://enternews.vn/phong-thuy-c329', 'https://enternews.vn/khoa-hoc-c330',
                  'https://enternews.vn/suc-khoe-c326', 'https://enternews.vn/doanh-nghiep-c11',
                  'https://enternews.vn/doanh-nghiep-24-7-c206', 'https://enternews.vn/ky-nang-quan-tri-c74',
                  'https://enternews.vn/doc-nhanh-c3', 'https://enternews.vn/nguon-nhan-luc-c208',
                  'https://enternews.vn/trach-nhiem-xa-hoi-c279',
                  'https://enternews.vn/chi-so-khung-nang-luc-doanh-nghiep-c287',
                  'https://enternews.vn/doanh-nghiep-tre-c296', 'https://enternews.vn/thuong-hieu-va-hoi-nhap-c207'
                  'https://enternews.vn/vcci-c8',
                  'https://enternews.vn/24h-c308',
                  'https://enternews.vn/phap-luat-c10',
                  'https://enternews.vn/tai-chinh-ngan-hang-c7',
                  'https://enternews.vn/kinh-te-vi-mo-c2',
                  'https://enternews.vn/tam-diem-c114','https://enternews.vn/mang-xa-hoi-c295',
                  'https://enternews.vn/cong-nghe-c243',
                  'https://enternews.vn/nguoi-viet-tu-te-c299',
                  ]
    base_url = 'https://enternews.vn/'

    def parse(self, response):

        top_item = response.xpath('//div[@class="top-item"]//h2/a').css('::attr(href)').get()
        if top_item:
            yield SeleniumRequest(url=top_item, callback=self.parse_post)

        scroll_news = response.xpath('//div[@id="top-news-scroll"]/ul/li//a[@class="font-16"]').css('::attr(href)')
        if scroll_news:
            for new in scroll_news:
                time.sleep(1)
                yield SeleniumRequest(url=new.extract(), callback=self.parse_post)

        posts = response.xpath('//ul[@class="feed"]/li/h2/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            yield SeleniumRequest(url=url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@class="btn btn-xs font-14 btn-primary"]')

        if next_page:
            next_url = response.xpath('//a[@class="btn btn-xs font-14 btn-primary"]').css('::attr(href)').get()
            yield SeleniumRequest(url=next_url)

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
        time_format, short_date = self.parse_date(response)
        content, html = self.parse_content(response)
        if response.xpath('//h1[@class="post-title main-title"]/text()').get():
            item = NewsItem(
                title=response.xpath('//h1[@class="post-title main-title"]/text()').get(),
                timestamp=time_format,
                content_html=content,
                body=html,
                link=response.url,
                subhead=response.xpath('//h2[@class="post-sapo"]/strong/text()').get(),
                pic=self.parse_pictures(response),
                date=short_date,
                author=''
            )
            yield item

    def parse_date(self, response):
        if response.xpath('//div[@class="post-author cl"]/span/text()').get():
            raw_time = response.xpath('//div[@class="post-author cl"]/span/text()').get().replace('| ', '').strip()
            true_time = parser.parse(raw_time)
            publish_date = datetime(year=true_time.year, minute=true_time.minute, hour=true_time.hour,
                                    day=true_time.day,
                                    month=true_time.month)
            return publish_date.isoformat(), '{}/{}/{}'.format(true_time.month, true_time.day, true_time.year)
        else:
            return '', ''

    def parse_pictures(self, response):
        urls = response.xpath('//img[@class="image_center"]/@src').extract()
        urls = [urljoin(self.base_url, item) for item in urls]
        captions = response.xpath('//img[@class="image_center"]/@alt').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    def parse_content(self, response):
        raw_text = response.xpath('//div[@class="post-content "]/p/text()').extract()
        raw_html = response.xpath('//div[@class="post-content "]/p').extract()
        return ' '.join(raw_text), ' '.join(raw_html)
