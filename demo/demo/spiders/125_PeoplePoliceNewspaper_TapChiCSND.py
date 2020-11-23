import re
import urllib.parse
from scrapy import Spider, Request
from datetime import datetime
from html2text import html2text

categories = [
    '/Home/An-ninh-trat-tu',
    '/Home/Nghien-cuu-Trao-doi',
    '/Home/Giao-duc-Dao-tao',
    '/Home/Thong-tin-ly-luan',
    '/Home/Quoc-te',
    '/Home/Dien-Dan',
]


class PeoplePoliceNewspaperSpider(Spider):
    name = 'PeoplePoliceNewspaper'
    allowed_domains = ['csnd.vn']
    start_urls = ['http://csnd.vn/']
    url_template = 'http://csnd.vn/{category}?page={page}'
    base_url = 'https://csnd.vn'

    def start_requests(self):
        for category in categories:
            url = self.url_template.format(category=category, page=1)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        posts = response.xpath("//div[@class='zoneteaser clearfix']/ul/li/h4/a/@href").extract()
        yield from response.follow_all(urls=posts, callback=self.parse_post)

        pages = response.xpath("//div[@class='zonepage-l']/div[@class='datapager']/a")
        filter_pages = filter(lambda page: page.xpath('text()').get().isdigit(), pages)
        page_urls = map(lambda page: page.xpath('@href').get(), filter_pages)
        yield from response.follow_all(page_urls, self.parse_page)

        next_page = response.xpath("//div[@class='datapager']/a[@class='next']/@href").get()
        if next_page:
            yield Request(url=urllib.parse.urljoin(self.base_url, next_page), callback=self.parse_page)

    def parse_page(self, response):
        posts = response.xpath("//div[@class='zoneteaser clearfix']/ul/li/h4/a/@href").extract()
        yield from response.follow_all(urls=posts, callback=self.parse_post)

    def parse_post(self, response):
        title = response.xpath("//div[@class='story_head clearfix']/span[@class='story_headline']/text()").get()
        subhead = response.xpath(
            "//div[@class='story_content clearfix']/div[@class='story_teaser']/p/span/text()").get() or \
                  response.xpath(
                      "//div[@class='story_content clearfix']/div[@class='story_teaser']/p/strong/span/text()").get() or \
                  ""
        body_html = response.xpath("//div[@class='story_content clearfix']/div[@class='story_body']").get()
        date_html = response.xpath("//div[@class='story_tools clearfix']/span[@class='story_date']/text()").get()
        day, month, year, *_ = re.findall(r'\d+', date_html)
        date = datetime(int(year), int(month), int(day)).strftime('%d/%m/%Y')
        yield {
            'date': date,
            'title': title.strip(),
            'subhead': subhead.strip(),
            'body': html2text(body_html),
            'author': '',
            'original_link': response.url,
            'print': '',
            'source': '',
            'pic_list': self.parse_pic(response),
            'site': '125_csnd'
        }

    def parse_pic(self, response):
        pics = []
        img_elements = response.xpath("//p/span/img")
        for index, img_element in enumerate(img_elements):
            src = urllib.parse.urljoin(self.base_url, img_element.xpath('@src').get())
            cap = img_element.xpath("../following-sibling::p[@style='text-align: center;'][1]/em/text()").get() or \
                  ""
            if index % 2 == 0:
                pics.append(f"{src}|{cap}")
            else:
                pics.append(f"{src}_{cap}")
        return "&&".join(pics)
