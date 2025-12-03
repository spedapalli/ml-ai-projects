from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from core import string_utils
from models.db.documents import UserDocument
from datapipe.crawlers.linkedin_crawler import LinkedInCrawler
from datapipe.crawlers.medium_crawler import MediumCrawler
from datapipe.crawlers.github_crawler import GithubCrawler
from datapipe.crawler_dispatcher import CrawlerDispatcher



logger = Logger(service="llm-twin-course/crawler")

### ------- for Debug purposes only --------
# import debugpy
# print("Waiting for debugger attach.....")
# debugpy.wait_for_client()
# print("Debugger attached!")
### ------- End Debug code -----------------

_dispatcher = CrawlerDispatcher()
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("github", GithubCrawler)

def handler(event, context: LambdaContext | None = None) -> dict[str, Any]:
    """ Entry point to AWS Lambda fn., when an event, such as new content published to
     GitHub or LinkedIn or Medium, triggers

    Args:
        event (_type_): Contains "user", "link" to the article,
        context (LambdaContext | None, optional): Defaults to None.

    Returns:
        dict[str, Any]: _description_
    """
    first_name, last_name = string_utils.split_user_full_name(event.get("user"))

    user_id = UserDocument.get_or_create(first_name = first_name, last_name=last_name)

    link = event.get('link')
    crawler = _dispatcher.get_crawler(link)

    try :
        crawler.extract(link=link, user=user_id)
        return {"statusCode": 200, "body": "Link processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred {str(e)}"}



if __name__ == "__main__":
    event = {
        "user": "Samba Pedapalli",
        "link": "https://linkedin.com/in/sambas"
    }
    handler(event, None)