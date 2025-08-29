from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from aws_lambda_powertools import Logger

from model.db.documents import ArticleDocument
from datapipe.crawlers.base_abstract_crawler import BaseAbstractCrawler


logger = Logger(service="llm-twin-course/crawler")

class MediumCrawler(BaseAbstractCrawler) :
    MEDIUM_SITE_URL = "https://medium.com/m/signin"

    model = ArticleDocument

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=profile 2")


    def extract(self, link:str, **kwargs) -> None:
        """ Given the link (from crawler), parses the Html to retrieve enough data to normalize and reference
        the article and load into NoSQL store.

        Args:
            link (str): URL of the published medium post
        """
        logger.info(f"Starting scraping of Medium article..... {link}")

        self.driver.get(link)
        self.scroll_page()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragprah")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        logger.info(f"Successfully scraped and saved article: {link}")
        self.driver.close()

        instance = self.model(platform ='medium',
                              content=data,
                              link=link,
                              author_id=kwargs.get("user"))
        instance.save()


    def login(self):
        """ login using Google """
        self.driver.get(self.MEDIUM_SITE_URL)
        self.driver.find_element(By.TAG_NAME, "a").click()

