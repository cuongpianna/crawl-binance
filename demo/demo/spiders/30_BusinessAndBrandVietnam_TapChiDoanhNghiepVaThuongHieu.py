import scrapy
from datetime import datetime
from dateutil import parser
import html2text

from demo.items import NewsItem

categories = {
    'su_kien_binh_luan': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyMjE2KQ',
    'thoi_su': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI4KQ',
    'quy_hoach_kien_truc': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDY1KQ',
    'bat_dong_san': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTE4KQ',
    'vat_lieu': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDYxKQ',
    'khoa_hoc_cong_nghe': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDk4KQ',
    'kinh_te': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTIxKQ',
    'xa_hoi': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTM2KQ',
    'phap_luat': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI5KQ',
    'ban_doc': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTMwKQ',
    'the_gioi': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTM1KQ',
    'van_hoa': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDkzKQ',
    'giai_tri': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI3KQ',
    'du_lich': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDI0KQ',
    'suc_khoe': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTQwKQ'
}


class BusinessAndBrandVietnamSpider(scrapy.Spider):
    name = 'BusinessAndBrandVietnam'
    site_name = 'doanhnghiepthuonghieu.vn'
    allowed_domains = ['doanhnghiepthuonghieu.vn']

    start_urls = [
        'https://doanhnghiepthuonghieu.vn/thoi-su', 'https://doanhnghiepthuonghieu.vn/thoi-su/tin-tuc-thoi-su',
        'https://doanhnghiepthuonghieu.vn/thoi-su/van-de-su-kien',
        'https://doanhnghiepthuonghieu.vn/thoi-su/lam-theo-loi-bac',
        'https://doanhnghiepthuonghieu.vn/thoi-su/quoc-hoi', 'https://doanhnghiepthuonghieu.vn/lien-ket',
        'https://doanhnghiepthuonghieu.vn/lien-ket/tin-tuc',
        'https://doanhnghiepthuonghieu.vn/lien-ket/su-kien-kien-binh-luan',
        'https://doanhnghiepthuonghieu.vn/lien-ket/nong-nghiep-nong-thon-toan-cau',
        'https://doanhnghiepthuonghieu.vn/lien-ket/cong-nghe', 'https://doanhnghiepthuonghieu.vn/nong-thon-viet',
        'https://doanhnghiepthuonghieu.vn/nong-thon-viet/so-tay',
        'https://doanhnghiepthuonghieu.vn/nong-thon-viet/nong-thon-xanh',
        'https://doanhnghiepthuonghieu.vn/nong-thon-viet/khuyen-nong',
        'https://doanhnghiepthuonghieu.vn/nong-thon-viet/nong-san-viet',
        'https://doanhnghiepthuonghieu.vn/kinh-te',
        'https://doanhnghiepthuonghieu.vn/kinh-te/tin-tuc-kinh-te',
        'https://doanhnghiepthuonghieu.vn/kinh-te/doanh-nghiep-doanh-nhan',
        'https://doanhnghiepthuonghieu.vn/kinh-te/doanh-nhan',
        'https://doanhnghiepthuonghieu.vn/kinh-te/thuong-hieu',
        'https://doanhnghiepthuonghieu.vn/kinh-te/bat-dong-san',
        'https://doanhnghiepthuonghieu.vn/nong-nghiep-4-0',
        'https://doanhnghiepthuonghieu.vn/nong-nghiep-4-0/khoa-hoc-cong-nghe',
        'https://doanhnghiepthuonghieu.vn/nong-nghiep-4-0/nhin-ra-the-gioi',
        'https://doanhnghiepthuonghieu.vn/tieu-dung',
        'https://doanhnghiepthuonghieu.vn/tieu-dung/cay-thuoc-vi-thuoc',
        'https://doanhnghiepthuonghieu.vn/tieu-dung/nguoi-tieu-dung-thong-thai',
        'https://doanhnghiepthuonghieu.vn/tieu-dung/bao-ve-nguoi-tieu-dung',
        'https://doanhnghiepthuonghieu.vn/tieu-dung/an-toan-thuc-pham',
        'https://doanhnghiepthuonghieu.vn/nhip-song',
        'https://doanhnghiepthuonghieu.vn/nhip-song/huyen-thuat',
        'https://doanhnghiepthuonghieu.vn/nhip-song/the-thao',
        'https://doanhnghiepthuonghieu.vn/nhip-song/do-thi-cuoc-song',
        'https://doanhnghiepthuonghieu.vn/nhip-song/song-tre',
        'https://doanhnghiepthuonghieu.vn/nhip-song/song-khoe',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat/chinh-sach-moi',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat/phap-luat',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat/van-ban-phap-luat',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat/hoi-dap-phap-lu%E1%BA%A1t',
        'https://doanhnghiepthuonghieu.vn/nhip-cau-phap-luat/ban-doc',
        'https://doanhnghiepthuonghieu.vn/media',
        'https://doanhnghiepthuonghieu.vn/media/anh',
    ]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def parse(self, response):
        hot_news = response.xpath('//div[@class="row  gutter-10 hot-cate"]//a[@class="link_unstyle"]/@href')
        posts = response.xpath('//ul[@class="list-post-cat-bottom"]/li/a/@href')

        if hot_news:
            for post in hot_news:
                url = post.extract()
                yield response.follow(url, callback=self.parse_post)

        if posts:
            for post in posts:
                url = post.extract()
                yield response.follow(url, callback=self.parse_post)

        next_page = response.xpath('//ul[@class="pagination"]/li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="col-md-12"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="col-md-12"]').get()),
            link=response.url,
            subhead=response.xpath('//div[@class="des f-roboto-b t-16-mb dt-des"]/text()').get(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        """

        :param response: format: 2020-09-09 12:18:20
        :return:
        """
        raw_time = response.xpath('//div[@class="col-6 info-author cl-737373"]/text()').extract()[1]
        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    @staticmethod
    def parse_pictures(response):
        if response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]/p//img/@src'):
            images = response.xpath(
                '//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]/p//img/@src').extract()
            captions = []
            for i, item in enumerate(images):
                caption = response.xpath(
                    '(//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]/p//img)[{}]/parent::p/following-sibling::p[1]//em/text()'.format(
                        i + 1)).get()
                caption = '' if not caption else caption
                captions.append(caption)
            res = [i + '|' + j for i, j in zip(images, captions)]
            result = '&&'.join(res)
            return result
        elif response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//table//img/@src'):
            images = response.xpath(
                '//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//table//img/@src').extract()
            captions = response.xpath(
                '//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//table//tr[2]/td').extract()
            captions = [html2text.html2text(item) for item in captions]
            res = [i + '|' + j for i, j in zip(images, captions)]
            result = '&&'.join(res)
            return result
        elif response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//figure//img/@src'):
            images = response.xpath(
                '//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//figure//img/@src').extract()
            captions = []
            for i, item in enumerate(images):
                caption = response.xpath(
                    '//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//figure[1]//figcaption'.format(
                        i + 1)).get()
                caption = '' if not caption else caption
                captions.append(caption)
            res = [i + '|' + j for i, j in zip(images, captions)]
            result = '&&'.join(res)
            return result
        return ''

    @staticmethod
    def parse_author(response):
        if response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]/p[last()]'):
            return html2text.html2text(
                response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]/p[last()]').get())
        elif response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//*[@class="article-bottom"]').get():
            return html2text.html2text(response.xpath('//div[@class="content content-mb mb-20 overflow-hidden t-16-mb"]//*[@class="article-bottom"]')).get()
        return ''

