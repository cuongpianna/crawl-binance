from scrapy import Spider, Request
import urllib.parse
from datetime import datetime
from html2text import html2text
import re

categories = {
    'thoi-su': '/cate/780/thoi-su.html',
    'vcci': '/cate/693/vcci.html',
    'doi-ngoai': '/cate/702/doi-ngoai.html',
    'kinh-te-thi-truong': '/cate/728/kinh-te-thi-truong.html',
    'xuat-nhap-khau': '/cate/714/xuat-nhap-khau.html',
    'dau-tu': '/cate/721/dau-tu.html',
    'tai-chinh': '/cate/707/tai-chinh.html',
    'doanh-nghiep': '/cate/734/doanh-nghiep.html',
    'bat-dong-san': '/cate/740/bat-dong-san.html',
    'cong-nghe': '/cate/746/cong-nghe.html',
    'van-hoa-du-lich': '/cate/751/van-hoa-du-lich.html',
}


class VietnamBusinessForumSpider(Spider):
    name = 'VietnamBusinessForum'
    site_name = 'vccinews.vn'
    allowed_domains = ['vccinews.vn']
    start_urls = ['https://vccinews.vn']

    base_url = 'https://vccinews.vn/'
    url_templates = 'https://vccinews.vn{path}'

    def __init__(self, page=1, *args, **kwargs):
        super(VietnamBusinessForumSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for category in categories.values():
            url = self.url_templates.format(path=category)
            urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.load_page_category)

    def load_page_category(self, response):
        other_news_btn = response.xpath("//div[@id='othernews']/p/input/@onclick").get()

        url = self.parse_btn_load_page(other_news_btn)
        if url is not None:
            yield Request(url=url, callback=self.parse_otherview_category)

    def parse_otherview_category(self, response):
        post_urls = response.xpath('//div[@id="othernews"]/ul/li/a/@href').extract()
        urls = [urllib.parse.urljoin(self.base_url, post_url) for post_url in post_urls]
        yield from response.follow_all(urls, self.parse_post)

        pre_input = response.xpath('//div[@id="othernews"]/table/tbody/tr/td[1]/input/@onclick').get()
        if pre_input is not None:
            pre_url = self.parse_btn_load_page(pre_input)
            yield Request(url=pre_url, callback=self.parse_pre_page)

        next_input = response.xpath('//td[@align="right"]/input/@onclick').get()
        if next_input is not None:
            pre_url = self.parse_btn_load_page(next_input)
            yield Request(url=pre_url, callback=self.parse_next_page)

    def parse_pre_page(self, response):
        post_urls = response.xpath('//div[@id="othernews"]/ul/li/a/@href').extract()
        urls = [urllib.parse.urljoin(self.base_url, post_url) for post_url in post_urls]
        yield from response.follow_all(urls, self.parse_post)

        pre_input = response.xpath('//td[@align="left"]/input/@onclick').get()
        if pre_input is not None:
            pre_url = self.parse_btn_load_page(pre_input)
            yield Request(url=pre_url, callback=self.parse_pre_page)

    def parse_next_page(self, response):
        post_urls = response.xpath('//div[@id="othernews"]/ul/li/a/@href').extract()
        urls = [urllib.parse.urljoin(self.base_url, post_url) for post_url in post_urls]
        yield from response.follow_all(urls, self.parse_post)

        next_input = response.xpath('//td[@align="right"]/input/@onclick').get()
        if next_input is not None:
            pre_url = self.parse_btn_load_page(next_input)
            yield Request(url=pre_url, callback=self.parse_next_page)

    def parse_post(self, response):
        content_html = response.xpath('//div[@class="detail-blog-page"]/div[@class="desc-ctn"]').get()
        timestamp = response.xpath('//div[@class="time"]/p/text()').get()
        return {
            'date': self.parse_timestamp(timestamp, 'date'),
            'timestamp': self.parse_timestamp(timestamp, 'iso'),
            'title': response.xpath('//div[@class="detail-blog-page"]/h1/text()').get().strip(),
            'subhead': response.xpath('//div[@class="detail-blog-page"]/h1/text()').get().strip(),
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(content_html),
            'content_html': content_html,
            'author': response.xpath('//div[@class="desc-ctn"]/p/span/span/span/em/strong/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/p/span/span/span/span/strong/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/p/em/strong/span/span/span/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/p/span/span/span/strong/em/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/p/span/span/em/strong/text()').get() or \
                      response.xpath(
                          '//div[@class="desc-ctn"]/div[@class="contentdetail"]/p/span/span/span/em/strong/text()').get() or \
                      response.xpath('//p[last()]/span/span/span/em/strong/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/div/p[last()]/b/span/text()').get() or \
                      response.xpath('//div[@class="desc-ctn"]/span/text()').get() or \
                      response.xpath('//span/span/span/em/span/strong/text()').get() or \
                      response.xpath('//*[@class="desc-ctn"]/p/i/span/text()').get() or \
                      response.xpath(
                          '(//*[@class="desc-ctn"]/div)[last()]//span[@style="font-weight: bold;"][last()]/text()').get()
        }

    @staticmethod
    def parse_pic(response):
        pic = ''
        img_elements = response.xpath('//span/span/span/img')
        images = []
        captions = []
        for img_element in img_elements:
            src = img_element.xpath('@src').get()
            caption = img_element.xpath('../../../../span/span/em/text()').get()
            pic += f'&&{src}_{caption}'
            images.append(src)
            captions.append(caption)
        result = [i + '|' + j for i, j in zip(images, captions)]
        pic = '&&'.join(result)
        return pic

    @staticmethod
    def parse_timestamp(timestamp, type_parse):
        if timestamp is None:
            return ''
        else:
            datetime_parse = datetime.strptime(timestamp.strip(), '%H:%M:%S %p | %d/%m/%Y')
            if type_parse is 'iso':
                return datetime_parse.isoformat()
            else:
                return datetime_parse.strftime('%d/%m/%Y')

    def parse_btn_load_page(self, input_btn):
        pattern = '\\((.*)\\)'
        match = re.search(pattern, input_btn)
        page_path = match.groups()[0].replace('\'', '').split(',')[0]
        return self.url_templates.format(path=page_path)
