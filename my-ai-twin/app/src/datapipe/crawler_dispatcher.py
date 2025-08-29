import re

from aws_lambda_powertools import Logger
from datapipe.crawlers.base_abstract_crawler import BaseCrawler
from datapipe.crawlers.custom_article_crawler import CustomArticleCrawler


logger = Logger(service="llm-twin-course/crawler")


class CrawlerDispatcher:

    def __init__(self) -> None:
        self._crawlers = {}


    def register(self, domain: str, crawler: type[BaseCrawler]) -> None :
        """ Registers a given domain and its associated Crawler class, a class which can crawl through the content
        from the pages on the domain website.
        Args:
            domain (str): The website domain eg: linkedin or medium
            crawler (type[BaseCrawler]): Crawler class that inherits from BaseCrawler and associated to above domain content.
        """
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler


    def get_crawler(self, url:str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()

            else :
                logger.warning(f"No crawler found for {url}. Defaulting to CustomArticleCrawler.")

                return CustomArticleCrawler()