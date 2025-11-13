# from typing import List
from enum import Enum
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.models import Batch

from db.qdrant_connection import QdrantDatabaseConnector
from models.db.documents import RepositoryDocument, ArticleDocument, PostDocument
from core.logger_utils import get_logger
from models.base_models import VectorDBDataModel

logger = get_logger(__name__)


class CleanDataEnum(Enum):
    POSTS = "cleaned_posts"
    ARTICLES = "cleaned_articles"
    REPOSITORIES = "cleaned_repositories"

class VectorDataEnum(Enum):
    POSTS = "vector_posts"
    ARTICLES = "vector_articles"
    REPOSITORIES = "vector_repositories"

class BytewaxQdrantOutput(DynamicSink):
    """ This class facilitates the connection to Qdrant Vector DB. Since it inherits DynamicSink, it supports concurrent writes.
    Inherits DynamicSink given the class ability to create both vector and non-vector collections in the DB
    """


    def __init__(self, connection: QdrantDatabaseConnector, sink_type: str):
        self._connection = connection
        self._sink_type = sink_type

        # initializing collections with value indicating if it is Vector collection or not
        # Note there are 2 sets for each posts, articles and repositories since we use Qdrant as our "clean data sink"
        collections = {
            "cleaned_posts" : False,
            "cleaned_articles" : False,
            "cleaned_repositories": False,
            "vector_posts": True,
            "vector_articles": True,
            "vector_repositories": True,
        }

        # check if collections exist
        for collection_name, is_vector in collections.items():
            try:
                self._connection.get_collection(collection_name=collection_name)
            except Exception as e:
                logger.warning(f"Unable to access the collection {collection_name}. Creating one...")

                # create the collection
                if is_vector:
                    self._connection.create_vector_collection(collection_name)
                else:
                    self._connection.create_non_vector_collection(collection_name)


    def build(self, step_id:str, worker_index:int, worker_count: int) -> StatelessSinkPartition:
        """Override this method to identify the type of sink object to create,
        based on the value assigned when this class is instantiated.

        Args:
            step_id (str): ignored
            worker_index (int): ignored
            worker_count (int): ignored

        Raises:
            ValueError: if this class _sink_type is not initialized with the 2 supported value, 'clean', 'vector'
            during instantiation

        Returns:
            StatelessSinkPartition: _description_
        """
        if self._sink_type == 'clean':
            return QdrantCleanedDataSink(connection=self._connection)
        elif self._sink_type == 'vector':
            return QdrantVectorDataSink(connection=self._connection)
        else:
            raise ValueError(f"Unsupported sink type: {self._sink_type}")


class QdrantCleanedDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection

    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        # unzip abv tuples into iteratables
        ids, data = zip(*payloads)
        # get collection name from type of data
        collection_name = get_clean_collection(data_type=data[0]['type'])
        self._client.write_data(collection_name=collection_name, points=Batch(ids=ids, vectors={}, payloads=data))

        logger.info(f"Successfully inserted cleaned data ", collection_name, num=len(ids))



class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection


    def write_batch(self, items: list[VectorDBDataModel]) -> None:
        payloads = [item.to_payload() for item in items]
        ids, vectors, metadata = zip(*payloads)
        # get collection name from metadata
        collection_name = get_vector_collection(data_type=metadata[0]['type'])

        self._client.write_data(collection_name=collection_name, points=Batch(ids=ids, vectors=vectors, payloads=metadata))

        logger.info("Successfully inserted vector data ", collection_name, num=len(ids))


def get_clean_collection(data_type:int) -> str:
    if data_type == PostDocument.Settings.name:
        return CleanDataEnum.POSTS.value
    elif data_type == ArticleDocument.Settings.name:
        return CleanDataEnum.ARTICLES.value
    elif data_type == RepositoryDocument.Settings.name:
        return CleanDataEnum.REPOSITORIES.value
    else :
        raise ValueError(f"Unsupported collection type {data_type}")


def get_vector_collection(data_type: int) -> str:
    if data_type == PostDocument.Settings.name:
        return VectorDataEnum.POSTS.value
    elif data_type == ArticleDocument.Settings.name:
        return VectorDataEnum.ARTICLES.value
    elif data_type == RepositoryDocument.Settings.name:
        return VectorDataEnum.REPOSITORIES.value
    else :
        raise ValueError(f"Unsupported collection type {data_type}")


