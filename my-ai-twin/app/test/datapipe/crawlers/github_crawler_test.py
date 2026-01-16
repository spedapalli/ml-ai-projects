import pytest

# IMPORTANT : Initialize to use mongodb on localhost before any module is imported. Else it defaults to docker instance
# TODO : TO run this in CICD pipeline will need to figure out where mongodb wud run and how to access it
from core.config import settings
settings.patch_localhost()

from datapipe.crawlers.github_crawler import GithubCrawler



def test_extract():
    link:str = "https://github.com/spedapalli/ml-ai-projects"
    user_id = "samba.pedapalli"

    crawler: GithubCrawler = GithubCrawler()
    print("extracting files from github......")
    crawler.extract(link, user=user_id)
