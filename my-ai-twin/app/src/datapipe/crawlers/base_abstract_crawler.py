import time
import random
from abc import ABC, abstractmethod
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

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

        # if below not included medium.com throws error
        options.add_argument("--enable-javascript")
        options.add_argument("--enable-cookies")
        # std set of options
        options.add_argument("--no-sandbox")    # disable the chrome sandbox security
        options.add_argument("--headless=new")  # New headless mode is harder to detect
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
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

        # Anti-detection settings
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option("useAutomationExtension", False)
        # options.add_argument("--disable-web-security")
        # options.add_argument("--allow-running-insecure-content")

        self.set_extra_driver_options(options)

        self.scroll_limit = scroll_limit

        # Use undetected-chromedriver to bypass bot detection
        self.driver = uc.Chrome(
            options=options,
            headless=True,
            version_main=143  # Match installed Chrome version
        )
        self.driver.set_window_size(1920, 1080)  # Common desktop resolution

        # Hide WebDriver property to evade detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Override navigator properties to appear more human
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        })


    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass


    def scroll_page(self) -> None:
        """Scroll page with random delays to mimic human behavior"""
        curr_scroll: int = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Random scroll amount (human-like behavior)
            scroll_amount = random.randint(300, 700)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

            # Random delay between scrolls (2-6 seconds)
            time.sleep(random.uniform(2, 6))

            # Sometimes scroll to bottom
            if random.random() > 0.5:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (
                self.scroll_limit and curr_scroll >= self.scroll_limit
            ):
                break
            last_height = new_height
            curr_scroll += 1


