from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from core.config import settings
from core.logger_utils import get_logger

logger = get_logger(__file__)


class MongoDatabaseConnector:
    """_summary_
    """

    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            try :
                logger.info(f"Database host url: {settings.MONGO_DATABASE_HOST}")
                cls._instance = MongoClient(settings.MONGO_DATABASE_HOST)
                logger.info(f"Connection to database with uri: {settings.MONGO_DATABASE_HOST} successful")

            except ConnectionFailure:
                logger.error(f"Couldnt connect to the database")
                raise

        return cls._instance


    def get_database(self):
        assert self._instance, "Database connection not initialized"

        return self._instance[settings.MONGO_DATABASE_NAME]


    def close(self):
        if self._instance:
            self._instance.close()
            logger.info("Successfully closed the MongoDB connection")
        else :
            logger.info("Database connection not initialized and hence nothing to close")


connection = MongoDatabaseConnector()