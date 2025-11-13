from abc import ABC, abstractmethod

from models.content_enum import ContentDataEnum
from models.base_models import DataModel
from models.chunk_models import PostChunkModel, ArticleChunkModel, RepositoryChunkModel
from models.db_vector_models import PostVectorDBModel, ArticleVectorDBModel, RepositoryVectorDBModel

from featurepipe.utils.embeddings_util import convert_text_to_embedding


class EmbeddingDataHandler(ABC):

    @abstractmethod
    def embed(self, data_model: DataModel) -> DataModel:
        pass


class PostEmbeddingHandler(EmbeddingDataHandler):
    def embed(self, data_model:PostChunkModel) -> PostVectorDBModel:
        return PostVectorDBModel(
            entry_id = data_model.entry_id,
            type = data_model.type,
            platform= data_model.platform,
            chunk_id= data_model.chunk_id,
            chunk_content= data_model.chunk_content,
            embedded_content= convert_text_to_embedding(data_model.chunk_content),
            author_id= data_model.author_id
        )


class ArticleEmbeddingHandler(EmbeddingDataHandler):

    def embed(self, data_model: ArticleChunkModel) -> ArticleVectorDBModel:
        return ArticleVectorDBModel(
            entry_id= data_model.entry_id,
            type= data_model.type,
            platform= data_model.platform,
            link= data_model.link,
            chunk_id= data_model.chunk_id,
            chunk_content= data_model.chunk_content,
            embedded_content= convert_text_to_embedding(data_model.chunk_content),
            author_id= data_model.author_id
        )


class RepositoryEmbeddingHandler(EmbeddingDataHandler) :

    def embed(self, data_model: RepositoryChunkModel) -> RepositoryVectorDBModel :
        return RepositoryVectorDBModel(
            entry_id= data_model.entry_id,
            type= data_model.type,
            name= data_model.name,
            link= data_model.link,
            chunk_id= data_model.chunk_id,
            chunk_content= data_model.chunk_content,
            embedded_content= convert_text_to_embedding(data_model.chunk_content),
            owner_id= data_model.owner_id,
        )


class EmbeddingHandlerFactory:

    @staticmethod
    def create_handler(data_type) -> EmbeddingDataHandler:
        if (data_type == ContentDataEnum.POSTS):
            return PostEmbeddingHandler()
        elif (data_type == ContentDataEnum.ARTICLES):
            return ArticleEmbeddingHandler()
        elif (data_type == ContentDataEnum.REPOSITORIES):
            return RepositoryEmbeddingHandler()
        else:
            raise ValueError(f"Embedding handler unsupported for data type {data_type}")


