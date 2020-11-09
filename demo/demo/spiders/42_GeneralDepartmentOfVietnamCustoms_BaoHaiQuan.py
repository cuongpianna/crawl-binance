import scrapy
from datetime import datetime
from scrapy import Request
from dateutil import parser

from demo.items import NewsItem

categories = {

}


class GeneralDepartmentOfVietnamCustomsSpider(scrapy.Spider):
    name = 'GeneralDepartmentOfVietnamCustoms'
    site_name = 'haiquanonline.com.vn'
    allowed_domains = ['haiquanonline.com.vn']

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    start_urls = ['https://haiquanonline.com.vn/thoi-su', 'https://haiquanonline.com.vn/thoi-su/doi-thoai',
                  'https://haiquanonline.com.vn/thoi-su/nguoi-quan-sat', 'https://haiquanonline.com.vn/quoc-te',
                  'https://haiquanonline.com.vn/quoc-te/hai-quan-the-gioi', 'https://haiquanonline.com.vn/hai-quan',
                  'https://haiquanonline.com.vn/hai-quan/chinh-sach-va-cuoc-song',
                  'https://haiquanonline.com.vn/hai-quan/hien-dia-hoa-hai-quan',
                  'https://haiquanonline.com.vn/hai-quan/nop-thue-dien-tu-247',
                  'https://haiquanonline.com.vn/an-ninh-xnk',
                  'https://haiquanonline.com.vn/tai-chinh/chinh-sach-moi',
                  'https://haiquanonline.com.vn/tai-chinh',
                  'https://haiquanonline.com.vn/tai-chinh/thue-kho-bac',
                  'https://haiquanonline.com.vn/tai-chinh/chung-khoan',
                  'https://haiquanonline.com.vn/kinh-te/thi-truong-gia-ca',
                  'https://haiquanonline.com.vn/kinh-te', 'https://haiquanonline.com.vn/kinh-te/nhip-do-phat-trien',
                  'https://haiquanonline.com.vn/kinh-te/xuat-nhap-khau',
                  'https://haiquanonline.com.vn/doanh-nghiep/ho-tro-dnxnk', 'https://haiquanonline.com.vn/doanh-nghiep',
                  'https://haiquanonline.com.vn/doanh-nghiep/doanh-nghiep-uu-tien',
                  'https://haiquanonline.com.vn/doanh-nghiep/so-huu-tri-tue',
                  'https://haiquanonline.com.vn/doi-song-do-thi',
                  'https://haiquanonline.com.vn/doi-song-do-thi/phong-su',
                  'https://haiquanonline.com.vn/doi-song-do-thi/ban-doc',
                  'https://haiquanonline.com.vn/du-lich/tour-ks',
                  'https://haiquanonline.com.vn/giai-tri', 'https://haiquanonline.com.vn/giai-tri/goc-nhin-van-hoa',
                  'https://haiquanonline.com.vn/o-to-xe-may', 'https://haiquanonline.com.vn/du-lich',
                  'https://haiquanonline.com.vn/du-lich/diem-den',
                  'https://haiquanonline.com.vn/du-lich/am-thuc'
                  ]

    def parse(self, response):

        top_news = response.xpath(
            '//div[@class="cover-top clearfix"]/div[contains(@class, "left")]/a[@class="box-img"]/@href').get()
        if top_news:
            yield Request(top_news, callback=self.parse_post)

        posts = response.xpath('//*[@id="main-stream"]/li/a').css('::attr(href)')
        if posts:
            for post in posts:
                url_extract = post.extract()
                yield response.follow(url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[text()=">"]/@href')

        if next_page:
            yield Request(next_page.get())

    def parse_post(self, response):

        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get().strip(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]').get(),
            body=self.parse_body(response),
            link=response.url,
            subhead=response.xpath('//p[@class="detail-sapo"]/text()').get().strip(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_body(self, response):
        text_list = response.xpath('//div[@class="__MB_MASTERCMS_EL item-content"]/p/text()').extract()
        result = ''.join(text_list)
        return result

    def parse_date(self, response):
        """
        Convert string to timestamp
        :param response: - Time format:  10:00 | 08/11/2020
        :return: timestamp, date
        """

        string_time = response.xpath('//span[@class="format_time"]/text()').get()
        string_date = response.xpath('//span[@class="format_date"]/text()').get()
        raw_time = string_time + ' ' + string_date
        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath(
            '//table[@class="MASTERCMS_TPL_TABLE"]//img/@src').extract()
        captions = response.xpath(
            '//table[@class="MASTERCMS_TPL_TABLE"]//tr[2]/td/text()').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        if response.xpath(
                '//div[@class="article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]/p/strong/text()').get():
            return response.xpath(
                '//div[@class="article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]/p/strong/text()').get().strip()
        else:
            return ''
