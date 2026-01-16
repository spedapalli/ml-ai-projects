import os
import shutil
import subprocess
import tempfile

# from aws_lambda_powertools import Logger
from core.logger_utils import get_logger
from models.db.documents import RepositoryDocument
from datapipe.crawlers.base_abstract_crawler import BaseCrawler


logger = get_logger(__file__)


class GithubCrawler (BaseCrawler):

    model = RepositoryDocument

    def __init__(self,
                 ignore=(".git", ".toml", ".lock", ".png", ".venv", ".pdf", \
                    "__pycache__", "__init__.py", "__init__.pyc", ".csv", ".pkl"),
                 ignore_dirs=("data", "data-analysis", "images", "logs", "temp")) -> None:
        """_summary_

        Args:
            ignore (tuple, optional): special files or dirs to ignore. Defaults to (".git", ".toml", ".lock", ".png").
            ignore_dirs (tuple, optional): Directories without any code such as data, data-analysis, images, logs, temp etc..
        """
        super().__init__()
        self._ignore = ignore
        self._ignore_dirs = ignore_dirs


    def extract(self, link: str, **kwargs) -> None:
        logger.info(f"Starting scraping of Github link: {link}")

        repo_name = link.rstrip("/").split("/")[-1] # get the last part of the URL i.e repo name
        local_temp = tempfile.mkdtemp()

        try :
            os.chdir(local_temp)
            subprocess.run(['git', 'clone', link], check=True, capture_output=True, text=True)

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0]) # get the project root dir

            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                # Ignore any dir that are in ignore list OR any dirs that are not in Process dir
                last_dir = dir.split("/")[-1]
                logger.info(f"Dir is : {dir}, and the last dir name is: {last_dir}")
                if (dir.startswith(self._ignore) or (last_dir in self._ignore_dirs) ):
                    logger.info(f"Repository files : Ignoring dir: {dir}")
                    continue

                tree = {}
                for file in files:
                    if (file.endswith(self._ignore)):
                        logger.info(f"Repository files : Ignoring file: {file}")
                        continue

                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), 'r', errors='ignore') as f:
                        tree[file_path] = f.read().replace(" ", "")

                if tree :
                    instance = self.model(
                        name = repo_name, link=link, content = tree, owner_id=kwargs.get('user')
                    )
                    # instance.save()

        except Exception as e:
            logger.error(f"Failed to scrape Github repo : {e}", exc_info=True)
            raise
        finally:
            shutil.rmtree(local_temp)

        logger.info(f"Finished scarping Github repo : {link}")
