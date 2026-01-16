from typing_extensions import deprecated
import time
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
    # vars to capture stats on batch embedding
    total_embedding_time = 0
    total_embedded_items = 0
    # vars to capture stats on each individual embedding
    single_total_embedding_time = 0
    single_total_embedded_items = 0

    @classmethod
    @deprecated("Use the batching function dispatch_batch_embedder(...)")
    def dispatch_embedder(cls, data_model:DataModel) -> DataModel:
        logger.info("In Embedding Dispatcher........")
        data_type = data_model.type
        handler: EmbeddingDataHandler = cls.embedding_factory.create_handler(data_type=data_type)

        # measure time
        start_time = time.perf_counter()
        embedded_chunk_model: DataModel = handler.embed(data_model=data_model)

        time_elapsed: int | float = time.perf_counter() - start_time
        cls.single_total_embedded_items += 1
        cls.single_total_embedding_time += time_elapsed

        logger.info("Data chunk embeddings created successfully ",
                    data_type=data_type,
                    embedding_len=len(embedded_chunk_model.embedded_content))
        logger.info(f"Stats to embed each item individually: Total # of items: {cls.single_total_embedded_items}, Total Time= {cls.single_total_embedding_time}")

        return embedded_chunk_model


    @classmethod
    def dispatch_batch_embedder(cls, batched_data: tuple[str, list[DataModel]]) -> tuple[str, list[DataModel]] :
        """Process embedding for batch of texts (chunks)

        Args:
            batched_data (tuple[str, list[DataModel]]): chuncked text

        Returns:
            tuple[str, list[DataModel]]: _description_
        """

        batch_key, data_models = batched_data
        if not data_models:
            return (batch_key, [])

        # all items in the batch must be same type
        data_type: str = data_models[0].type
        handler: EmbeddingDataHandler = cls.embedding_factory.create_handler(data_type)

        # measure total time
        start_time: int | float = time.perf_counter()
        embeds_models = handler.embed_batch(data_models=data_models)
        time_elapsed: int | float = time.perf_counter() - start_time


        cls.total_embedding_time += time_elapsed
        cls.total_embedded_items += len(embeds_models)

        logger.info(f"Batch embedded {len(embeds_models)} chunks", data_type=data_type)
        logger.info(f"Total time to embed a total of {cls.total_embedded_items} items, so far, is= {cls.total_embedding_time}")

        return (batch_key, embeds_models)


