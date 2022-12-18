import json

import scrapy
from scrapy.http import TextResponse


class BusinessSpiderSpider(scrapy.Spider):
    name = "business"
    allowed_domains = ["www.yelp.com"]

    BASE_URL = "https://www.yelp.com"
    SEARCH_URL = BASE_URL + "/search/snippet"
    REVIEW_PARAMS = {"rl": "en", "sort_by": "relevance_desc"}
    REVIEWS_COUNT = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.search_params = {
            "find_desc": input("Input category name (for example: contractors)\n>>> "),
            "find_loc": input("Input location (for example: San Francisco, CA)\n>>> "),
            "start": "0"
        }

    def start_requests(self):
        urls = [
            self.SEARCH_URL,
        ]

        for url in urls:
            yield scrapy.FormRequest(
                url=url,
                method="GET",
                formdata=self.search_params,
                callback=self.parse,
            )

    def parse(self, response: TextResponse, **kwargs):
        response_dict = json.loads(response.text)

        # Create a list of businesses while filtering out sponsored results.
        result_list = [
            result for result
            in response_dict["searchPageProps"]["mainContentComponentsListProps"]
            if "bizId" in result and result["searchResultBusiness"]["isAd"] is False
        ]

        for result in result_list:
            business = result["searchResultBusiness"]
            business_id = result["bizId"]
            review_url = f"{self.BASE_URL}/biz/{business_id}/review_feed"

            yield scrapy.FormRequest(
                url=review_url,
                method="GET",
                formdata=self.REVIEW_PARAMS,
                callback=self.parse_reviews,
                meta={
                    "id": business_id,
                    "name": business["name"],
                    "url": f"{self.BASE_URL}{business['businessUrl']}",
                    "rating": business["rating"],
                    "review_count": business["reviewCount"],
                    "phone": business["phone"],
                }
            )

    def parse_reviews(self, response: TextResponse, **kwargs):
        response_dict = json.loads(response.text)

        reviews_list = response_dict["reviews"][:self.REVIEWS_COUNT]

        yield {
            "id": response.meta["id"],
            "name": response.meta["name"],
            "url": response.meta["url"],
            "rating": response.meta["rating"],
            "review_count": response.meta["review_count"],
            "phone": response.meta["phone"],
            "reviews": [
                {
                    "reviewer name": review["user"]["markupDisplayName"],
                    "reviewer location": review["user"]["displayLocation"],
                    "date": review["localizedDate"],
                }
                for review in reviews_list
            ]
        }
