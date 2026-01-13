from core.logger_utils import get_logger
from models.content_enum import ContentDataEnum
from models.base_models import DataModel
from models.raw_models import PostRawModel, ArticleRawModel, RepositoryRawModel

from featurepipe.datalogic.chunking_data_handlers import ChunkingHandlerFactory
from featurepipe.datalogic.cleaning_data_handlers import CleaningHandlerFactory
from featurepipe.datalogic.embedding_data_handlers import EmbeddingHandlerFactory, EmbeddingDataHandler


logger = get_logger(__name__)

class RawDispatcher:
    @staticmethod
    def handle_mq_message(message: dict) -> DataModel:
        data_type = message.get("type")
        logger.info(f"Received MQ message of data type: {data_type}")

        if data_type == ContentDataEnum.POSTS:
            return PostRawModel(**message)
        elif data_type == ContentDataEnum.ARTICLES:
            return ArticleRawModel(**message)
        elif data_type == ContentDataEnum.REPOSITORIES:
            return RepositoryRawModel(**message)
        else:
            raise ValueError(f"Unsupported MQ message data type: {data_type}")



class CleaningDispatcher:
    cleaning_factory = CleaningHandlerFactory()

    @classmethod
    def dispatch_cleaner(cls, data_model:DataModel) -> DataModel:
        data_type = data_model.type

        handler = cls.cleaning_factory.create_handler(data_type=data_type)
        clean_model = handler.clean(data_model=data_model)

        logger.info("Data cleaned successfully,", data_type=data_type, cleaned_content_len=len(clean_model.cleaned_content))

        return clean_model


class ChunkingDispatcher:
    chunk_factory = ChunkingHandlerFactory()

    @classmethod
    def dispatch_chunker(cls, data_model: DataModel) -> list[DataModel]:
        data_type = data_model.type

        handler = cls.chunk_factory.create_handler(data_type=data_type)
        chunk_models = handler.chunk(data_model=data_model)

        logger.info("Cleaned Data chunked successfully.", data_type=data_type, chunked_content_len=len(chunk_models))

        return chunk_models



class EmbeddingDispatcher:
    embedding_factory = EmbeddingHandlerFactory()   #class var

    @classmethod
    def dispatch_embedder(cls, data_model:DataModel) -> DataModel:
        logger.info("In Embedding Dispatcher........")
        data_type = data_model.type
        handler: EmbeddingDataHandler = cls.embedding_factory.create_handler(data_type=data_type)
        embedded_chunk_model: DataModel = handler.embed(data_model=data_model)

        logger.info("Data chunk embeddings created successfully ",
                    data_type=data_type,
                    embedding_len=len(embedded_chunk_model.embedded_content))

        return embedded_chunk_model