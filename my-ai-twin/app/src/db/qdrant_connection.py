from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Batch, Distance, VectorParams

from core import logger_utils
from core.config import settings

logger = logger_utils.get_logger(__name__)


class QdrantDatabaseConnector:
    _instance:QdrantClient | None = None

    def __init__(self) -> None:
        if self._instance is None:
            if settings.USE_QDRANT_CLOUD:
                self._instance = QdrantClient(
                    url=settings.QDRANT_CLOUD_URL,
                    api_key=settings.QDRANT_API_KEY
                )
            else :
                self._instance = QdrantClient(
                    host=settings.QDRANT_DATABASE_HOST,
                    port=settings.QDRANT_DATABASE_PORT
                )

    def get_collection(self, collection_name:str):
        return self._instance.get_collection(collection_name=collection_name)


    def create_non_vector_collection(self, collection_name:str):
        """Creates a basic non-vector collection

        Args:
            collection_name (str): collection name
        """
        try:
            self._instance.create_collection(collection_name=collection_name, vectors_config={})
        except Exception as e :
            logger.error(f"Failed to create non-vector collection {collection_name} given the exception ")
            logger.exception(e)
            raise e


    def create_vector_collection(self, collection_name:str):
        """ Creates a vector collection with embeddings: dimensionality size=348 (core.config.settings.EMBEDDING_SIZE)
        and distance=COSINE.
        """
        try:
            self._instance.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_SIZE, distance=Distance.COSINE))
        except Exception as e:
            logger.error(f"Failed to create Vector collection {collection_name} given the exception ")
            logger.exception(e)
            raise e


    def write_data(self, collection_name: str, points: Batch):
        """upsert data into the DB

        Args:
            collection_name (str): the collection to write to
            points (Batch): unit of data to write consisting of unique id, a vector and payload (metadata)
        """
        try :
            self._instance.upsert(collection_name=collection_name, points=points)
        except Exception as e :
            logger.exception(f"An error occurred while upserting data to collection {collection_name}")
            raise

    def search(self,
               collection_name:str,
               query_vector:list,
               query_filter:models.Filter | None=None,
               limit:int = 3) -> list :

        response = self._instance.query_points(collection_name=collection_name,
                                               query=query_vector,
                                               query_filter=query_filter,
                                               limit=limit)
        return response.points

    def scroll(self, collection_name:str, limit:int):
        return self._instance.scroll(collection_name=collection_name, limit=limit)

    def close(self):
        if self._instance:
            self._instance.close()
            logger.info("Qdrant database connection closed")
