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
