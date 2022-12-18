import json
from urllib.parse import urljoin

import scrapy
from scrapy.http import TextResponse


class BusinessSpiderSpider(scrapy.Spider):
    name = "business"
    allowed_domains = ["www.yelp.com"]
    start_urls = [
        "https://www.yelp.com/search/snippet?find_desc=Delivery&find_loc=San+Francisco%2C+CA&start=0",
    ]

    def parse(self, response: TextResponse, **kwargs):
        response_dict = json.loads(response.text)

        # Create a list of businesses while filtering out sponsored results.
        result_list = [
            result
            for result in response_dict["searchPageProps"][
                "mainContentComponentsListProps"
            ]
            if "bizId" in result and result["searchResultBusiness"]["isAd"] is False
        ]

        for result in result_list:
            business = result["searchResultBusiness"]
            yield {
                "id": result["bizId"],
                "name": business["name"],
                "url": urljoin(self.allowed_domains[0], business["businessUrl"]),
                "rating": business["rating"],
                "review_count": business["reviewCount"],
                "phone": business["phone"],
            }
