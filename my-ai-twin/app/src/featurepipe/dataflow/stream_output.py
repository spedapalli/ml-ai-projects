# from typing import List
from enum import Enum
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from qdrant_client.models import PointStruct

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

    def write_batch(self, items: list[tuple[str, list[VectorDBDataModel]]]) -> None:
        logger.info(f"List of tuoles received for Vector models= {len(items)}")
        # loop thrugh list
        for items_tup in items:
            logger.info(f"QdrantCleanedDataSink.write_batch: received item type {type(items_tup)}, of size: {len(items_tup)}")
            # logger.info(f"Tuple contents: content1: {items_tup[0]}, content2: {items_tup[1]}")
            # the first element is a string identifying the batch which we ignore. Second element is VectorDBModel eg: RepositoryDBCleanedModel
            doc_items:list = items_tup[1]
            logger.info(f"Batch items in Tuple received for Vector models= {len(doc_items)}")
            # to_payload() of VectorDBModel returns a tuple
            payloads = [item.to_payload() for item in doc_items]
            # ids, data = zip(*payloads)
            # # get collection name from type of data
            # collection_name = get_clean_collection_name(data_type=data[0]['type'])
            # self._client.write_data(collection_name=collection_name, points=Batch(ids=ids, vectors={}, payloads=data))

            point_structs: list[PointStruct] = [
                PointStruct(id=payload[0],
                            vector={},
                            payload= payload[1] if payload[1] is not None else {}
                        ) for payload in payloads
            ]
            # get datatype from the first PointStruct, meta field assuming datatype is identical across
            data_type: str = point_structs[0].payload['type']
            collection_name = get_vector_collection_name(data_type)

            self._client.write_batch_data(collection_name=collection_name, points_batch=point_structs)
            logger.info(f"Successfully inserted cleaned data {collection_name},  num={len(point_structs)}")



class QdrantVectorDataSink(StatelessSinkPartition):
    def __init__(self, connection: QdrantDatabaseConnector):
        self._client = connection


    def write_batch(self, items: list[tuple[str, list[VectorDBDataModel]]]) -> None:
        logger.info(f"List of tuples received for Vector models= {len(items)}")
        for batch_tup in items :
            logger.info(f"Batch size received for Vector models= {len(batch_tup)}")
            # the first element is a string identifying the batch which we ignore
            batch_items: list = batch_tup[1]
            logger.info(f"Batch items in Tuple received for Qdrant Vector Collection= {len(batch_items)}")
            payloads = [item.to_payload() for item in batch_items]
            # ids, vectors, metadata = zip(*payloads)
            # collection_name = get_vector_collection_name(data_type=metadata[0]['type'])
            # self._client.write_data(collection_name=collection_name, points=Batch(ids=ids, vectors=vectors, payloads=metadata))

            point_structs: list[PointStruct] = [
                PointStruct(id=payload[0],
                            vector=payload[1],
                            payload= payload[2] if payload[2] is not None else {}
                        ) for payload in payloads
            ]

            # get datatype from the first PointStruct, meta field assuming datatype is identical across
            data_type: str = point_structs[0].payload['type']
            collection_name = get_vector_collection_name(data_type)

            logger.info(f"Data being inserted into Qdrant has # of Ids= {len(point_structs)}")

            self._client.write_batch_data(collection_name, points_batch=point_structs)

            logger.info(f"Successfully inserted vector data : {collection_name}, num={len(point_structs)}")



def get_clean_collection_name(data_type:int) -> str:
    if data_type == PostDocument.Settings.name:
        return CleanDataEnum.POSTS.value
    elif data_type == ArticleDocument.Settings.name:
        return CleanDataEnum.ARTICLES.value
    elif data_type == RepositoryDocument.Settings.name:
        return CleanDataEnum.REPOSITORIES.value
    else :
        raise ValueError(f"Unsupported collection type {data_type}")


def get_vector_collection_name(data_type: int) -> str:
    if data_type == PostDocument.Settings.name:
        return VectorDataEnum.POSTS.value
    elif data_type == ArticleDocument.Settings.name:
        return VectorDataEnum.ARTICLES.value
    elif data_type == RepositoryDocument.Settings.name:
        return VectorDataEnum.REPOSITORIES.value
    else :
        raise ValueError(f"Unsupported collection type {data_type}")


