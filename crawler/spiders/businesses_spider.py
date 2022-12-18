import json
from urllib.parse import urljoin

import scrapy
from scrapy.http import TextResponse


class BusinessSpiderSpider(scrapy.Spider):
    name = "business"
    allowed_domains = ["www.yelp.com"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.search_params = {
            "find_desc": input("Input category name (for example: contractors)\n>>> "),
            "find_loc": input("Input location (for example: San Francisco, CA)\n>>> "),
        }

    def start_requests(self):
        urls = [
            "https://www.yelp.com/search/snippet",
        ]

        for url in urls:
            yield scrapy.FormRequest(
                url=url,
                method="GET",
                formdata=self.search_params,
                callback=self.parse
            )

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
                "url": response.urljoin(business["businessUrl"]),
                "rating": business["rating"],
                "review_count": business["reviewCount"],
                "phone": business["phone"],
            }
