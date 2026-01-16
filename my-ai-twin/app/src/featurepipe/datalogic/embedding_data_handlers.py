
from typing import Any
import time
import numpy as np
from typing_extensions import deprecated
from abc import ABC, abstractmethod

from models.content_enum import ContentDataEnum
from models.base_models import DataModel
from models.chunk_models import PostChunkModel, ArticleChunkModel, RepositoryChunkModel
from models.db_vector_models import PostVectorDBModel, ArticleVectorDBModel, RepositoryVectorDBModel

from featurepipe.utils.embeddings_util import batch_encode_text, batch_encode_code_using_BGE, convert_text_to_embedding, convert_repotext_to_embedding_BGE

from core.logger_utils import get_logger

logger = get_logger(__name__)

class EmbeddingDataHandler(ABC):

    # repo_code_model: AbsEmbedder = FlagAutoModel.from_finetuned(settings.EMBEDDING_MODEL_FOR_CODE_ID)

    @abstractmethod
    def embed(self, data_model: DataModel) -> DataModel:
        pass

    def embed_batch(self, data_models: list[DataModel]) -> list[DataModel]:
        return [self.embed(dm) for dm in data_models]


class PostEmbeddingHandler(EmbeddingDataHandler):
    @deprecated("Please use embed_batch function")
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

    def embed_batch(self, data_models: list[PostChunkModel]) -> list[PostVectorDBModel] :
        start_time: int | float = time.perf_counter()
        texts: list[str] = [dm.chunk_content for dm in data_models]

        # batch encode all
        embeddings: np.ndarray[tuple[Any, ...], dtype[Any]] = batch_encode_text(texts)
        end_time: int | float = time.perf_counter()
        logger.info(f"Time to convert text to embeddings: {end_time - start_time}")

        # create models with pre-computed embeddings
        return [
            PostVectorDBModel(
                    entry_id = data_model.entry_id,
                    type = data_model.type,
                    platform= data_model.platform,
                    chunk_id= data_model.chunk_id,
                    chunk_content= data_model.chunk_content,
                    embedded_content= embeds_text,
                    author_id= data_model.author_id
            ) for data_model, embeds_text in zip(data_models, embeddings)
        ]


class ArticleEmbeddingHandler(EmbeddingDataHandler):

    @deprecated("Please use embed_batch function")
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

    def embed_batch(self, data_models: list[ArticleChunkModel]) -> list[ArticleVectorDBModel]:
        start_time: int | float = time.perf_counter()
        texts: list[str] = [dm.chunk_content for dm in data_models]

        # batch encode to embeddings
        embeddings: np.ndarray[tuple[Any, ...], dtype[Any]] = batch_encode_text(texts)
        end_time: int | float = time.perf_counter()
        logger.info(f"Time to convert {len(texts)} no of texts to embeddings: {end_time - start_time}")

        # create model
        return [
            ArticleVectorDBModel(
                    entry_id= data_model.entry_id,
                    type= data_model.type,
                    platform= data_model.platform,
                    link= data_model.link,
                    chunk_id= data_model.chunk_id,
                    chunk_content= data_model.chunk_content,
                    embedded_content= embeds_text,
                    author_id= data_model.author_id
            ) for data_model, embeds_text in zip(data_models, embeddings)
        ]


class RepositoryEmbeddingHandler(EmbeddingDataHandler) :

    @deprecated("Please use embed_batch function")
    def embed(self, data_model: RepositoryChunkModel) -> RepositoryVectorDBModel :
        """
        Embeds the repository chunk content using the model in #featurepipe.utils.embeddings_util.py.
        """
        logger.info("In Repository Embedding Handler........")
        return RepositoryVectorDBModel(
            entry_id= data_model.entry_id,
            type= data_model.type,
            name= data_model.name,
            link= data_model.link,
            chunk_id= data_model.chunk_id,
            chunk_content= data_model.chunk_content,
            # embedded_content= convert_text_to_embedding(data_model.chunk_content),
            embedded_content= convert_repotext_to_embedding_BGE(self.repo_code_model, data_model.chunk_content),
            owner_id= data_model.owner_id,
        )

    def embed_batch(self, data_models: list[RepositoryChunkModel]) -> list[RepositoryVectorDBModel] :

        start_time: int | float = time.perf_counter()
        texts: list[str] = [dm.chunk_content for dm in data_models]

        # batch embed
        embeddings: np.ndarray[tuple[Any, ...], dtype[Any]] = batch_encode_code_using_BGE(texts)

        end_time: int | float = time.perf_counter()
        logger.info(f"Time to convert {len(texts)} no of texts to embeddings: {end_time - start_time}")

        return [
            RepositoryVectorDBModel(
                entry_id= data_model.entry_id,
                type= data_model.type,
                name= data_model.name,
                link= data_model.link,
                chunk_id= data_model.chunk_id,
                chunk_content= data_model.chunk_content,
                # embedded_content= convert_text_to_embedding(data_model.chunk_content),
                embedded_content= embeds_text,
                owner_id= data_model.owner_id,
            ) for data_model, embeds_text in zip(data_models, embeddings)
        ]


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


