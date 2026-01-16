from abc import ABC, abstractmethod

from models.content_enum import ContentDataEnum
from models.base_models import DataModel
from models.db_clean_models import PostDBCleanedModel, ArticleDBCleanedModel, RepositoryDBCleanedModel
from models.raw_models import PostRawModel, ArticleRawModel, RepositoryRawModel
from featurepipe.utils.text_cleaning_util import normalize_text
from core.logger_utils import get_logger


logger = get_logger(__file__)

class CleaningDataHander(ABC):

    @abstractmethod
    def clean(self, data_model:DataModel) -> DataModel:
        '''
        Implementation of this method must ensure the returned DataModel object has the following attributes :
        entry_id, cleaned_content, author_id, type. These are critical for downstream Handler's processing.
        '''
        pass


class PostCleaningHander(CleaningDataHander) :

    def clean(self, data_model: PostRawModel) -> PostDBCleanedModel:

        joined_text = "".join(data_model.content.values()) if data_model.content else None
        return PostDBCleanedModel(
            entry_id = data_model.entry_id,
            platform = data_model.platform,
            cleaned_content = normalize_text(joined_text),
            author_id = data_model.author_id,
            image = data_model.image if data_model.image else None,
            type = data_model.type,
        )


class ArticleCleaningHandler(CleaningDataHander):

    def clean(self, data_model: ArticleRawModel) -> ArticleDBCleanedModel:
        logger.debug(f"Article Raw Data model: {data_model}")

        # if data_model.content is not None :
        joined_text = "".join(
            (value for value in data_model.content.values()
                if value is not None) if data_model.content else "")

        # joined_text = "".join(data_model.content.values()) if data_model.content else None

        model = ArticleDBCleanedModel(
            entry_id = data_model.entry_id,
            platform = data_model.platform,
            link = data_model.link,
            cleaned_content = normalize_text(joined_text),
            author_id = data_model.author_id,
            type = data_model.type
        )
        return model



class RepositoryCleaningHandler(CleaningDataHander):

    def clean(self, data_model: RepositoryRawModel) -> RepositoryDBCleanedModel:
        joined_text = "".join(data_model.content.values()) if data_model and data_model.content else None

        model = RepositoryDBCleanedModel(
            entry_id = data_model.entry_id,
            name = data_model.name,
            link = data_model.link,
            cleaned_content = normalize_text(joined_text),
            owner_id = data_model.owner_id,
            type = data_model.type,
        )
        return model


class CleaningHandlerFactory:

    @staticmethod
    def create_handler(data_type) -> CleaningDataHander:
        if data_type == ContentDataEnum.POSTS:
            return PostCleaningHander()
        elif data_type == ContentDataEnum.ARTICLES:
            return ArticleCleaningHandler()
        elif data_type == ContentDataEnum.REPOSITORIES:
            return RepositoryCleaningHandler()
        else :
            raise ValueError(f"CleaningHander unsupported for given data type: {data_type}")

