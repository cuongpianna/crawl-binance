import scrapy


class NewsItem(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    content_html = scrapy.Field()
    timestamp = scrapy.Field()
    print = scrapy.Field()
    original_link = scrapy.Field()
    subhead = scrapy.Field()
    pic_list = scrapy.Field()
    date = scrapy.Field()
    source = scrapy.Field()
    site = scrapy.Field()


class ProjectItem(scrapy.Item):
    Crypt = scrapy.Field()
    Name = scrapy.Field()
    Tagline = scrapy.Field()
    Date = scrapy.Field()
    Description = scrapy.Field()
    TokenSummary = scrapy.Field()
    AdditionalFeatures = scrapy.Field()
    # EconomicsAndSupplyDistribution = scrapy.Field()
    # ProjectTeam = scrapy.Field()
    # ActivityAndCommunityOverview = scrapy.Field()
    # SocialActivity = scrapy.Field()
    Website = scrapy.Field()
    Explorer = scrapy.Field()
    SourceCode = scrapy.Field()
    TechnicalDocument = scrapy.Field()
    # AdditionalResources = scrapy.Field()


class FilmItem(scrapy.Item):
    name = scrapy.Field()
    cates = scrapy.Field()
    categories_id = scrapy.Field()


class ProductItem(scrapy.Item):
    name = scrapy.Field()
    cate = scrapy.Field()
    images = scrapy.Field()
    features = scrapy.Field()
    brand = scrapy.Field()
    sku = scrapy.Field()
    rate = scrapy.Field()
    description = scrapy.Field()
    category_id = scrapy.Field()
    features = scrapy.Field()
    included = scrapy.Field()
    specifications = scrapy.Field()
    global_link = scrapy.Field()


class EastWoodItem(scrapy.Item):
    name = scrapy.Field()
    cate = scrapy.Field()
    images = scrapy.Field()
    features = scrapy.Field()
    brand = scrapy.Field()
    sku = scrapy.Field()
    rate = scrapy.Field()
    description = scrapy.Field()
    category_id = scrapy.Field()
    features = scrapy.Field()
    included = scrapy.Field()
    specifications = scrapy.Field()
    global_link = scrapy.Field()
    detail = scrapy.Field()
    long_description = scrapy.Field()
    contents = scrapy.Field()


class WelderItem(scrapy.Item):
    name = scrapy.Field()
    cate = scrapy.Field()
    images = scrapy.Field()
    features = scrapy.Field()
    brand = scrapy.Field()
    sku = scrapy.Field()
    rate = scrapy.Field()
    description = scrapy.Field()
    category_id = scrapy.Field()
    features = scrapy.Field()
    included = scrapy.Field()
    specifications = scrapy.Field()
    global_link = scrapy.Field()
