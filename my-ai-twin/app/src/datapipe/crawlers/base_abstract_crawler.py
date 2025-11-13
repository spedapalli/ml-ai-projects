import time
from abc import ABC, abstractmethod
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from models.db.base_document import BaseDocument

"""
Base class that captures base functionality used by source specific web scraper(s).
"""

class BaseCrawler(ABC):
    model: type[BaseDocument]

    @abstractmethod
    def extract(self, link: str, **kwargs) -> None: ...


class BaseAbstractCrawler(BaseCrawler, ABC) :

    def __init__(self, scroll_limit: int = 5) -> None:
        options: Options = webdriver.ChromeOptions()

        options.add_argument("--no-sandbox")    # disable the chrome sandbox security
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage") # in containers, use alt shared memory over default dev/shm
        options.add_argument("--log-level=3")   # log level = FATAL
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9226")

        self.set_extra_driver_options(options)

        self.scroll_limit = scroll_limit
        self.driver = webdriver.Chrome(
            options = options,
        )


    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass


    def scroll_page(self) -> None:

        curr_scroll: int = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (
                self.scroll_limit and curr_scroll >= self.scroll_limit
            ):
                break
            last_height = new_height
            curr_scroll += 1


