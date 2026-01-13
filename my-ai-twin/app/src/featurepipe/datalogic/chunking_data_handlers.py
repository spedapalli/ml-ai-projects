import hashlib
from abc import ABC, abstractmethod

from models.content_enum import ContentDataEnum
from models.base_models import DataModel
from models.db_clean_models import PostDBCleanedModel, ArticleDBCleanedModel, RepositoryDBCleanedModel
from models.chunk_models import PostChunkModel, ArticleChunkModel, RepositoryChunkModel
from featurepipe.utils.text_chunking_util import chunk_text
from core.logger_utils import get_logger

logger = get_logger(__name__)

class ChunkingDataHandler(ABC):

    @abstractmethod
    def chunk(self, data_model: DataModel) -> list[DataModel] :
        pass


class PostChunkingHandler(ChunkingDataHandler) :

    def chunk(self, data_model: PostDBCleanedModel) -> list[PostChunkModel]:
        data_models_list = []

        text_content = data_model.cleaned_content
        chunks = chunk_text(text_content)

        for chunk in chunks:
            model = PostChunkModel(
                entry_id=data_model.entry_id,
                type=data_model.type,
                platform=data_model.platform,
                chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
                image=data_model.image if data_model.image else None,
            )

            data_models_list.append(model)

        return data_models_list


class ArticleChunkingHandler(ChunkingDataHandler):

    def chunk(self, data_model: ArticleDBCleanedModel) -> list[ArticleChunkModel]:
        data_models_list = []

        text = data_model.cleaned_content
        chunks = chunk_text(text=text)

        for chunk in chunks:
            model = ArticleChunkModel(
                entry_id=data_model.entry_id,
                type=data_model.type,
                platform=data_model.platform,
                link = data_model.link,
                chunk_id= hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content=chunk,
                author_id=data_model.author_id,
            )

            data_models_list.append(model)

        return data_models_list


class RepositoryChunkingHandler(ChunkingDataHandler):

    def chunk(self, data_model: RepositoryDBCleanedModel) -> list[RepositoryChunkModel]:
        logger.info("In Repository Chunking Handler.......")

        data_models_list = []

        text = data_model.cleaned_content
        chunked_text = chunk_text(text)

        for chunk in chunked_text :
            model = RepositoryChunkModel(
                entry_id=data_model.entry_id,
                type= data_model.type,
                name= data_model.name,
                link = data_model.link,
                chunk_id = hashlib.md5(chunk.encode()).hexdigest(),
                chunk_content = chunk,
                owner_id=data_model.owner_id,
            )

            data_models_list.append(model)

        return data_models_list



class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_type) -> ChunkingDataHandler:
        if (data_type == ContentDataEnum.POSTS):
            return PostChunkingHandler()
        elif (data_type == ContentDataEnum.ARTICLES):
            return ArticleChunkingHandler()
        elif (data_type == ContentDataEnum.REPOSITORIES):
            return RepositoryChunkingHandler()
        else :
            raise ValueError("Unsupported chunking handler data")


