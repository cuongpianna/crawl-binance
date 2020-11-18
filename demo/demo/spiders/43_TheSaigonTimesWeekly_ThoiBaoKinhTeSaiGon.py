import scrapy
from datetime import datetime
import html2text
from dateutil import parser

from demo.items import NewsItem

categories = {

}


class TheSaigonTimesWeeklySpider(scrapy.Spider):
    name = 'TheSaigonTimesWeekly'
    site_name = 'thesaigontimes.vn'
    allowed_domains = ['thesaigontimes.vn']
    base_url = 'https://thesaigontimes.vn/'

    start_urls = ['https://www.thesaigontimes.vn/tieudiem/',
                  'https://diaoc.thesaigontimes.vn/dothi/nhadat/',
                  'https://diaoc.thesaigontimes.vn/dothi/hatang/',
                  'https://diaoc.thesaigontimes.vn/dothi/nhadat/',
                  'https://diaoc.thesaigontimes.vn/dothi/hatang/',
                  'https://diaoc.thesaigontimes.vn/dothi/vatlieucongnghe/',
                  'https://diaoc.thesaigontimes.vn/dothi/khonggiansong/',
                  'https://www.thesaigontimes.vn/Chu-de/374/',
                  'https://www.thesaigontimes.vn/doanhnghiep/guongmat/',
                  'https://www.thesaigontimes.vn/doanhnghiep/quantri/',
                  'https://www.thesaigontimes.vn/doanhnghiep/motvongdoanhnghiep/',
                  'https://www.thesaigontimes.vn/taichinh/dulieutaichinh/',
                  'https://diaoc.thesaigontimes.vn/dothi/duan/',
                  'https://www.thesaigontimes.vn/khoinghiep/startup/',
                  'https://www.thesaigontimes.vn/kinhdoanh/thuongmaidientu/',
                  'https://www.thesaigontimes.vn/Chu-de/392/',
                  'https://www.thesaigontimes.vn/doanhnghiep/chuyenlaman/',
                  'https://www.thesaigontimes.vn/taichinh/',
                  'https://www.thesaigontimes.vn/vanhoaxahoi/',
                  'https://www.thesaigontimes.vn/kinhdoanh/',
                  'thesaigontimes.vn/khoinghiep/',
                  'https://www.thesaigontimes.vn/thegioi/'
                  ]

    def parse(self, response):

        posts = response.xpath('//a[@class="ArticleTitle"]').css('::attr(href)')
        if posts:
            for post in posts:
                url_extract = post.extract()
                yield response.follow(url_extract, callback=self.parse_post)

        next_page = response.xpath('//*[contains(text(),"Xem tiếp")]')

        if next_page:
            yield response.follow(next_page.get())

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//*[@id="ARTICLEVIEW"]//p[@class="SGTOTitle"]/text()').get(),
            body=html2text.html2text(response.xpath('//*[@class="Content"]').get()),
            original_link=response.url,
            subhead=response.xpath('//div[@id="ARTICLEVIEW"]//*[@class="SGTOSummary"]/text()').get().strip(),
            pic_list=self.parse_pictures(response),
            date=short_date,
            author=author,
            site='43_thoi_bao_kinh_te_sai_gon',
            source='',
            print=''
        )
        yield item

    def parse_date(self, response):
        """
        Convert string to timestamp
        :param response: - Time format: Thứ Sáu,  6/11/2020, 14:34
        :return: timestamp, date
        """

        raw_time = response.xpath('//*[@class="Date"]/text()').get().replace(' ', '')
        converted_time = parser.parse(raw_time.split(',',1)[1].strip())
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//*[@class="desktop"]//div[@id="ARTICLEVIEW"]//*[@class="sgtoimagemiddle"]//img/@src').extract()
        captions = response.xpath(
            '//*[@class="desktop"]//div[@id="ARTICLEVIEW"]//*[@class="sgtoimagemiddle"]//tbody/tr[2]/td/text()').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        if response.xpath('//*[@class="ReferenceSourceTG"]/text()').get():
            return response.xpath(
                '//*[@class="ReferenceSourceTG"]/text()').get().strip()
        elif response.xpath('//*[@class="ReferenceSource"]/text()'):
            return response.xpath('//*[@class="ReferenceSource"]/text()').get()
        else:
            return ''
