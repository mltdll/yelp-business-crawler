import scrapy


class BusinessesSpiderSpider(scrapy.Spider):
    name = 'businesses_spider'
    allowed_domains = ['www.yelp.com']
    start_urls = ['http://www.yelp.com/']

    def parse(self, response):
        pass
