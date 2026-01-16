import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from aws_lambda_powertools import Logger

from models.db.documents import ArticleDocument
from datapipe.crawlers.base_abstract_crawler import BaseAbstractCrawler
from datetime import datetime


logger = Logger(service="llm-twin-course/crawler")

class MediumCrawler(BaseAbstractCrawler) :
    MEDIUM_SITE_URL = "https://medium.com/m/signin"

    model = ArticleDocument

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")


    def extract(self, link:str, **kwargs) -> None:
        """ Given the link (from crawler), parses the Html to retrieve enough data to normalize and reference
        the article and load into NoSQL store.

        Args:
            link (str): URL of the published medium post
        """
        logger.info(f"Starting scraping of Medium article..... {link}")

        self.login()

        # Random delay before navigating to article (1-3 seconds)
        time.sleep(random.uniform(1, 3))

        self.driver.get(link)

        # Wait for page to load and give time for JS to execute
        time.sleep(random.uniform(3, 5))

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

        try:
            # Wait for and click the "Sign in with Google" button
            # Try multiple selectors in case Medium's UI changes
            signin_button = None

            # Try finding by text content (most reliable)
            try:
                signin_button = WebDriverWait(self.driver, 10).until(
                    # EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'signin')]"))
                    # EC.element_to_be_clickable(By.XPATH, "//a[@data-testid='headerSignInButton' and text()='Sign in'][1]")
                    # TODO : Although the result is predicated, it still seems to return 2 records.
                    # TODO : This query returns only 1 when executed on webpage console. Need to debug further
                    EC.element_to_be_clickable(By.XPATH, "(//a[contains(@href, 'signin?operation=login')])[1]")
                    # EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign in with Google')]"))
                )
                signin_button.click()
                google_signin_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(By.XPATH, "//button[contains(@aria-label, 'Google')]")
                )
            except Exception as ex:
                logger.error(f"Failed to find or click sign-in button: {ex}")
                # Fallback: try finding by button with Google in aria-label
                google_signin_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(By.XPATH, "//button[contains(@aria-label, 'Google')]")
                )

            # Random delay before clicking (human-like)
            time.sleep(random.uniform(0.5, 1.5))
            google_signin_button.click()
            logger.info("Successfully clicked Sign in with Google button")

            # Wait for redirect/page load
            time.sleep(random.uniform(2, 4))

        except Exception as e:
            logger.error(f"Failed to find or click sign-in button: {e}")
            raise
