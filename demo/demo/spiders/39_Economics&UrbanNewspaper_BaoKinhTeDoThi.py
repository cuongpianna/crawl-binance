import scrapy
from datetime import datetime
from dateutil import parser
import html2text
from demo.items import NewsItem

categories = {

}


class EconomicsAndUrbanNewspaperSpider(scrapy.Spider):
    name = 'EconomicsAndUrbanNewspaper'
    site_name = 'kinhtedothi.vn'
    allowed_domains = ['kinhtedothi.vn']

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    start_urls = ['http://kinhtedothi.vn/chinh-tri/tin-tuc/',
                  'http://kinhtedothi.vn/chinh-tri/nghi-quyet-dang-vao-cuoc-song',
                  'http://kinhtedothi.vn/chinh-tri/cai-cach-hanh-chinh/',
                  'http://kinhtedothi.vn/thoi-su/nam-ky-cuong-hanh-chinh-2019/',
                  'http://kinhtedothi.vn/thoi-su/theo-guong-bac-ho',
                  'http://kinhtedothi.vn/kinh-te/thi-truong-tai-chinh/',
                  'http://kinhtedothi.vn/kinh-te/nguoi-viet-dung-hang-viet/',
                  'http://kinhtedothi.vn/kinh-te/thi-truong/',
                  'http://kinhtedothi.vn/doanh-nghiep/tin-tuc/',
                  'http://kinhtedothi.vn/kinh-te/doanh-nghiep/khoi-nghiep/',
                  'http://kinhtedothi.vn/do-thi/',
                  'http://kinhtedothi.vn/bat-dong-san/thi-truong/',
                  'http://kinhtedothi.vn/bat-dong-san/phong-thuy/',
                  'http://kinhtedothi.vn/bat-dong-san/do-thi-cuoc-song/',
                  'http://kinhtedothi.vn/bat-dong-san/tu-van-dau-tu/', 'http://kinhtedothi.vn/phap-luat/tin-tuc/',
                  'http://kinhtedothi.vn/phap-luat/phap-dinh/', 'http://kinhtedothi.vn/phap-luat/van-ban-chinh-sach/',
                  'http://kinhtedothi.vn/ban-doc/', 'http://kinhtedothi.vn/xa-hoi/doi-song/',
                  'http://kinhtedothi.vn/xa-hoi/giao-duc/', 'http://kinhtedothi.vn/thoi-su/tin-quan-huyen/',
                  'http://kinhtedothi.vn/xa-hoi/nguoi-tot-viec-tot/',
                  'http://kinhtedothi.vn/y-te/',
                  'http://kinhtedothi.vn/the-thao/',
                  'http://kinhtedothi.vn/van-hoa/tin-tuc/',
                  'http://kinhtedothi.vn/van-hoa/giai-tri/',
                  'http://kinhtedothi.vn/van-hoa/van-nghe/',
                  'http://kinhtedothi.vn/phong-su-anh/goc-anh-ha-noi-dep-va-chua-dep/',
                  'http://kinhtedothi.vn/van-hoa/ha-noi-thanh-lich-van-minh/',
                  'http://kinhtedothi.vn/quoc-te/tin-tuc/',
                  'http://kinhtedothi.vn/quoc-te/su-kien-binh-luan/',
                  'http://kinhtedothi.vn/quoc-te/kinh-te-tai-chinh-toan-cau/',
                  'http://kinhtedothi.vn/quoc-te/cac-do-thi-tren-the-gioi/',
                  'http://kinhtedothi.vn/cong-nghe/san-pham-so/',
                  'http://kinhtedothi.vn/cong-nghe/tin-tuc/',
                  'http://kinhtedothi.vn/du-lich/am-thuc/',
                  'http://kinhtedothi.vn/du-lich/su-kien/',
                  'http://kinhtedothi.vn/du-lich/kham-pha/',
                  'http://kinhtedothi.vn/du-lich/tour-hay/',
                  'http://kinhtedothi.vn/ha-noi-doc-va-la/'
                  ]

    def parse(self, response):

        top_news = response.xpath(
            '//div[@class="col440 fl  border_right"]//div[@class="pkg mar_bottom20"]/a/@href').get()
        if top_news:
            yield response.follow(top_news, callback=self.parse_post)

        posts = response.xpath('//ul[@class="list_news_topcate"]/li/a').css('::attr(href)')
        if posts:
            for post in posts:
                url_extract = post.extract()
                yield response.follow(url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@class="active"]//following-sibling::a[1]/@href')

        if next_page:
            yield response.follow(next_page.get())

    def parse_post(self, response):

        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get().strip(),
            timestamp=time_format,
            content_html=response.xpath(
                '//*[@id="cotent_detail"]').get(),
            body=self.parse_body(response),
            link=response.url,
            subhead=response.xpath('//div[@class="sapo_detail fr"]/text()').get().strip(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_body(self, response):
        return html2text.html2text(response.xpath('//*[@id="cotent_detail"]').get())

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

    @staticmethod
    def parse_pictures(response):
        """
        Get list pictures with their caption
        :param response:
        :return:
        """
        urls = response.xpath('//*[@class="picture"]//img/@src').extract()
        captions = response.xpath(
            '//*[@class="picture"]//div[@class="box_img_detail"]/center//img/@title-image').extract()
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
        if response.xpath('//span[@class="name_author fl"]/text()').get():
            return response.xpath('//span[@class="name_author fl"]/text()').get()
        else:
            return ''
