from scrapy import Spider, Request
from datetime import datetime
from html2text import html2text

categories = [
    'thoi-su/xay-dung-dang/',
    'trong-nuoc/',
    'quoc-te/',
    'xa-hoi/guong-sang-tham-lang-vi-cong-dong/',
    'xa-hoi/nghe-ctxh/',
    'nguoi-co-cong/',
    'an-sinh-xa-hoi/',
    'tre-em/',
    'phong-chong-tnxh/',
    'binh-dang-gioi/',
    'nghien-cuu-trao-doi/',
    'giao-duc-nghe-nghiep/',
    'doanh-nghiep/',
    'thi-truong-tieu-dung/',
    'tai-chinh-bat-dong-san/',
    'van-ban-phap-luat/',
    'phap-luat/giai-dap-phap-luat/',
    'van-hoa/',
    'giai-tri/',
    'the-thao/',
    'du-lich/',
    'suc-khoe-doi-song/',
    'english-review/',
]


class LaoDongXaHoiSpider(Spider):
    name = 'JournalOfLaborAndSocialAffairs'
    allowed_domains = ['laodongxahoi.net']
    start_urls = ['http://laodongxahoi.net/']
    base_url = 'http://laodongxahoi.net/'
    url_template = 'http://laodongxahoi.net/{}page/{}'

    def start_requests(self):
        for category in categories:
            url = self.url_template.format(category, 1)
            yield Request(url, self.parse)

    def parse(self, response):
        top_post = response.xpath(
            '//div[@class="pkg"]/div[@class="col420 fl border_right"]/div[@class="pkg"]/a[@class="f24 fontRobotoB mar5"]/@href').get()

        if top_post is not None:
            urls = response.xpath("//div[@class='fl info_cate']/a[@class='fontRobotoB f18']/@href").extract()
            urls.append(top_post)
            second_post = response.xpath("//div[@class='col240 fr']/a[@class='f16 fontRobotoB mar_bottom10']/@href").get()
            if second_post is not None:
                urls.append(second_post)
            for url in urls:
                yield response.follow(url, self.parse_post)
        else:
            return

    def parse_post(self, response):
        timestamp = response.xpath("//div[@class='pkg']/div/div[@class='time_detail_news f11']/text()").get()
        date = datetime.strptime(timestamp.strip(), '%H:%M %p %d/%m/%Y').strftime('%d/%m/%Y')
        title = response.xpath("//div[@class='title_detail_news']/text()").get()
        body_html = response.xpath("//div[@id='cotent_detail']/div").get()
        subhead = response.xpath("//div[@class='pkg']/div[@class='sapo_detail fr']/text()").get()
        author = self.parse_author(response)

        yield {
            'date': date,
            'title': title.strip(),
            'subhead': subhead.strip(),
            'body': html2text(body_html),
            'author': author.strip(),
            'original_link': response.url,
            'print': '',
            'source': '',
            'pic_list': self.parse_pic(response),
            'site': '130_nguoidothi'
        }

    @staticmethod
    def parse_pic(response):
        pics = []
        img_elements = response.xpath("//div[@id='cotent_detail']/div/center/img/@src").extract()
        for index, img_element in enumerate(img_elements):
            src = img_element
            cap = response.xpath('(//div[@id="cotent_detail"]/div/center/img)[{}]/..//following-sibling::*/text()'.format(index + 1))
            if index % 2 == 0:
                pics.append(f"{src}|{cap}")
            else:
                pics.append(f"{src}_{cap}")
        return "&&".join(pics)

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath("//div[@class='col660 fl bg_white']/div[@id='cotent_detail']/*[@style='text-align: right;']").get():
            return html2text(
                response.xpath("//div[@class='col660 fl bg_white']/div[@id='cotent_detail']/*[@style='text-align: right;']").get())
        return ''
