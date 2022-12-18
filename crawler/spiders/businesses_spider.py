import json
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy.http import TextResponse


class BusinessSpiderSpider(scrapy.Spider):
    name = "business"
    allowed_domains = ["www.yelp.com"]

    BASE_URL = "https://www.yelp.com"
    SEARCH_URL = BASE_URL + "/search/snippet"
    REVIEW_PARAMS = {"rl": "en", "sort_by": "relevance_desc"}
    REVIEWS_COUNT = 5
    META_KEYS = ["name", "url", "rating", "review_count", "phone", "website", "reviews"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.search_params = {
            "find_desc": input("Input category name (for example: contractors).\n>>> "),
            "find_loc": input("Input location (for example: San Francisco, CA).\n>>> "),
            "start": "0",
        }

        self.pages_to_scrape = int(input("Input amount of pages to scrape.\n>>> "))

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
            result
            for result in response_dict["searchPageProps"][
                "mainContentComponentsListProps"
            ]
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
                    "name": business["name"],
                    "url": f"{self.BASE_URL}{business['businessUrl']}",
                    "rating": business["rating"],
                    "review_count": business["reviewCount"],
                    "phone": business["phone"],
                    "website": None,
                },
            )

        # Continue scraping if more pages remain to be scraped.
        pagination = self._get_pagination_info(response_dict)

        if self._check_next_page(pagination):
            start_result = {
                "start": str(pagination["startResult"] + pagination["resultsPerPage"])
            }

            yield scrapy.FormRequest(
                url=self.SEARCH_URL,
                method="GET",
                formdata=self.search_params | start_result,
                callback=self.parse,
            )

    def parse_reviews(self, response: TextResponse, **kwargs):
        """Adds reviews to the output"""

        response_dict = json.loads(response.text)

        reviews_list = response_dict["reviews"][: self.REVIEWS_COUNT]

        reviews_dict = {
            "reviews": [
                {
                    "reviewer name": review["user"]["markupDisplayName"],
                    "reviewer location": review["user"]["displayLocation"],
                    "date": review["localizedDate"],
                }
                for review in reviews_list
            ],
        }

        yield scrapy.Request(
            url=response.meta["url"],
            callback=self.parse_website,
            meta=response.meta | reviews_dict,
        )

    def parse_website(self, response: TextResponse):
        website_url = response.css("a[href^='/biz_redir']").xpath("@href").get()

        if website_url is not None:
            parsed_url = urlparse(website_url)
            website_url = parse_qs(parsed_url.query)["url"][0]

        meta = {
            key: value for key, value in response.meta.items() if key in self.META_KEYS
        }

        yield meta | {"website": website_url}

    @staticmethod
    def _get_pagination_info(response_dict: dict) -> dict[str, int]:
        """Gets pagination info from JSON response dictionary"""

        content = response_dict["searchPageProps"]["mainContentComponentsListProps"]
        pagination = next(item for item in content if item.get("type") == "pagination")

        return pagination["props"]

    def _check_next_page(self, pagination: dict) -> bool:
        """
        Returns True if next page is available and not greater than max page
        permitted, otherwise returns False.
        """

        page_number = pagination["startResult"] // pagination["resultsPerPage"] + 1
        results_left = pagination["totalResults"] - pagination["startResult"]

        return (
            page_number < self.pages_to_scrape
            and results_left > pagination["resultsPerPage"]
        )
