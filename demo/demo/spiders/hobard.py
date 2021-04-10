from scrapy import Spider
from datetime import datetime
from demo.items import WelderItem
from scrapy_selenium import SeleniumRequest
import os
import urllib.parse
from urllib.request import urlretrieve
dir_path = os.path.dirname(os.path.realpath(__file__))


class IMDBSpider(Spider):
    name = 'HobartSpider'
    urls = ['https://www.hobartwelders.com/equipment/welders/stick-smaw',
            'https://www.hobartwelders.com/equipment/welders/engine-driven',
            'https://www.hobartwelders.com/equipment/plasma-cutters',
            'https://www.hobartwelders.com/equipment/welders/mig-gmaw',
            ]

    base_url = 'https://www.hobartwelders.com/'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': os.path.join(os.path.abspath(os.curdir), 'chromedriver.exe'),
        'SELENIUM_DRIVER_ARGUMENTS': ['headless', '-start-maximized']

    }

    def __init__(self, *args, **kwargs):
        self.driver = None
        super().__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        top_post = response.xpath('//div[@id="products-list"]//div[@class="image"]/a/@href')

        for post in top_post:
            url = urllib.parse.urljoin(self.base_url, post.get())
            yield SeleniumRequest(url=url, callback=self.parse_post)


    def parse_post(self, response):
        item = WelderItem(
            name=response.xpath('//h1[@id="product-subtitle"]/text()').get().strip(),
            cate=response.xpath('//div[@class="breadcrumb-trail"]//ul/li[7]/a/text()').get().strip(),
            brand='Hobart',
            sku=response.xpath('//span[@id="product-sku"]/text()').get().strip(),
            rate=response.xpath('//*[@class="pr-snippet-rating-decimal"]/text()').get().strip() if response.xpath(
                '//*[@class="pr-snippet-rating-decimal/text()"]') else 0,
            description=response.xpath('//*[@class="sales-copy"]/text()').get().strip(),
            images=self.parse_images(response),
            features=self.parse_features(response),
            included=self.parse_included(response),
            specifications=self.parse_specifications(response),
            global_link=response.request.url

        )
        yield item

    def parse_specifications(self, response):
        process = response.xpath('//div[@id="processes-list"]/div[@class="process single-item"]/text()').extract()
        process = [item.strip() for item in process]
        title = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Title")]/following-sibling::td/text()').get()
        industries_interests = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Industries Interests")]/following-sibling::td/text()').get()
        material_thickness = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Material Thickness")]/following-sibling::td/text()').get()
        weldable_metals = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Weldable Metals")]/following-sibling::td/text()').get()
        input_voltage = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Input Voltage")]/following-sibling::td/text()').get()
        input_phase = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Input Phase")]/following-sibling::td/text()').get()
        input_hz = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Input Hz")]/following-sibling::td/text()').get()
        input_amperage = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Input Amperage")]/following-sibling::td/text()').get()
        current_type = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Current Type")]/following-sibling::td/text()').get()
        rated_output = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Rated Output")]/following-sibling::td/text()').get()
        max_open_circuit_voltage = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Max Open Circuit Voltage")]/following-sibling::td/text()').get()
        wire_feed_speed = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Wire Feed Speed")]/following-sibling::td/text()').get()

        wire_diameter = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Wire Diameter")]/following-sibling::td/text()').get()
        portability = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Portability")]/following-sibling::td/text()').get()
        weld_output = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Weld Output")]/following-sibling::td/text()').get()
        net_width = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Net Width")]/following-sibling::td/text()').get()
        net_height = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Net Height")]/following-sibling::td/text()').get()
        net_weight = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Net Weight")]/following-sibling::td/text()').get()
        Warranty = response.xpath(
            '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Warranty")]/following-sibling::td/text()').get()

        general = dict(
            process=process if process else [],
            application=industries_interests.strip() if industries_interests else '',
            weldable_metals=weldable_metals.strip() if weldable_metals else '',
            material_thickness=material_thickness.strip() if material_thickness else '',
            weld_output=weld_output.strip() if weld_output else ''
        )

        input_value = dict(
            input_voltage=input_voltage.strip() if input_voltage else '',
            input_phase=input_phase.strip() if input_phase else '',
            input_frequency=input_hz.strip() if input_hz else '',
            input_current=input_amperage.strip() if input_amperage else '',
            max_incrush_amps=''
        )

        spool_gun = dict(
            spool_gun_capable='',
            drive_roll_wire_size='',
            number_of_driver_rollers='',
            wire_feed_speed=wire_feed_speed.strip() if wire_feed_speed else '',
            wire_roll_diameter=wire_diameter.strip() if wire_diameter else '',
        )

        output_value = dict(
            output_range=rated_output.strip() if rated_output else '',
            open_circuit_voltage=max_open_circuit_voltage.strip() if max_open_circuit_voltage else '',
            current_type=current_type.strip() if current_type else '',
            duty_cycle=response.xpath(
                '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Rated Output")]/following-sibling::td/text()').get(),
            max_current_output=response.xpath(
                '//div[@id="general-specifications-list"]//table//tr/th[contains(text(),"Rated Output")]/following-sibling::td/text()').get()
        )

        physical = dict(
            portability=portability.strip() if portability else '',
            dimension_width=net_width.strip() if net_width else '',
            dimension_height=net_height.strip() if net_height else '',
            dimension_weight=net_weight.strip() if net_weight else '',
            warranty=Warranty.strip() if Warranty else '',
        )

        result = dict(
            general=general,
            title=title.strip() if title else '',
            input=input_value,
            spool_gun=spool_gun,
            output=output_value,
            physical=physical,
            other_features=None
        )
        return result

    def parse_images(self, response):
        directory = "images"
        path = os.path.join(dir_path, directory)
        if not os.path.exists(path):
            os.makedirs(path)
        images = response.xpath('//div[@class="thumbs"]//li[@style="display: inline-block;"]//img/@src').extract()
        images = set(images)
        result = []
        for img in images:
            if img:
                image_url = urllib.parse.urljoin(self.base_url, img)
                image_url = image_url.replace('mw=70', 'mw=600')
                image_url = image_url.replace('mh=70', 'mw=600')
                dt = datetime.now()
                seq = dt.strftime("%Y%m%d%H%M%S")
                img_path = os.path.join(path, seq + '.png')
                urlretrieve(image_url, img_path)
                result.append(seq + '.png')
        return result

    def parse_included(self, response):
        included = response.xpath('//div[@class="included"]/ul//li/text()').extract()
        return included

    def parse_features(self, response):
        self.driver = response.meta['driver']
        features = self.driver.find_elements_by_xpath('//div[@class="features"]//div[@Class="feature-description"]')
        results = []
        for feature in features:
            results.append(feature.get_attribute('innerHTML'))
        return features
