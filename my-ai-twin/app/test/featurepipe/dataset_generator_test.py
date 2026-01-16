import pytest
import os
from dotenv import load_dotenv

from core.logger_utils import get_logger
from core.config import settings
# IMPORTANT : Initialize to use mongodb on localhost before any module using MongoDB is imported
# TODO : TO run this in CICD pipeline will need to figure out where mongodb wud run and how to access it
settings.patch_localhost()

from featurepipe.datasetgen.dataset_generator import DatasetGenerator
from featurepipe.datasetgen.dataformatter import DataFormatter
from featurepipe.datasetgen.gpt_communicator import GPTCommunicator
from featurepipe.utils.json_helper import JSONFileHandler

logger = get_logger(__name__)

# try:
# load_dotenv(dotenv_path="./.env")
# except:
#     logger.error(f"Unable to load the .env file {os.path.abspath('./.env')}")

def test_generate_data():
    json_handler = JSONFileHandler()
    gpt_communicator = GPTCommunicator()
    data_formatter = DataFormatter()
    dataset_generator = DatasetGenerator(json_handler, data_formatter, gpt_communicator)

    logger.info(f"COMET_API_KEY {os.environ.get('COMET_API_KEY')}")
    collections = [
        ("cleaned_articles", "articles"),
        ("cleaned_repositories", "repositories"),
    ]

    for collection_name, data_type in collections:
        logger.info(
            "Generated training data",
            collection_name = collection_name,
            data_type = data_type,
        )

        dataset_generator.generate_training_data(collection_name=collection_name, data_type=data_type)

