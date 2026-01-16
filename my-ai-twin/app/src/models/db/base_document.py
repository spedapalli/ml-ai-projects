import uuid
from typing import List, Optional

from pydantic import BaseModel, UUID4, ConfigDict, Field
from pymongo import errors

import core.logger_utils as logger_utils
from db.mongo import connection
from core.errors import ImproperlyConfigured
from core.config import settings


_database = connection.get_database(settings.MONGO_DATABASE_NAME)
logger = logger_utils.get_logger(__name__)

class BaseDocument(BaseModel) :

    id: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        """Retrieves the MongoDB record, given dict of input param

        Args:
            data (dict): Must contain the property 'id'

        Returns:
            _type_: If data is None, returns None. Else the object associated with the given Id in the params
        """
        if not data:
            return None

        id = data.pop("_id", None)
        return cls(**dict(data, id = id))


    def to_mongo(self, **kwargs) -> dict:
        """Converts input document to MongoDB format. Input param (kwargs) must contain either 'id'
        (msg id) or '_id' (DB id). Currently this function does not throw an error but queries can
        silently fail.
        Returns:
            dict: of properties including the message content and either 'id' or '_id' property.
        """
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(
            exclude_unset = exclude_unset, by_alias= by_alias, **kwargs
        )

        if "_id" not in parsed or id in parsed:
            parsed['_id'] = str(parsed.pop('id'))

        return parsed


    def save(self, **kwargs):
        """ Persists the input param, single record, into MongoDB

        Returns:
            _type_: Id of the persisted record
        """
        collection = _database[self._get_collection_name()]

        try:
            result = collection.insert_one(self.to_mongo(**kwargs))
            return result.inserted_id
        except errors.WriteError:
            logger.exception()
            raise


    @classmethod
    def get_or_create(cls, **filter_options) -> Optional[str]:
        """Upsert function. Checks if record with given 'id' in the param filter_options exists.
        If yes, returns the record, else creates one.

        Returns:
            Optional[str]: Id of the record
        """
        collection = _database[cls._get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                db_doc = cls.from_mongo(instance)
                if db_doc is not None:
                    return str(db_doc.id)

            new_instance = cls(**filter_options)
            new_instance = new_instance.save()
            return new_instance
        except errors.OperationFailure :
            logger.exception("Failed to retrieve or create document")
            return None


    @classmethod
    def find(cls, **filter_options):
        collection = _database[cls._get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            return None
        except errors.OperationFailure:
            logger.error("Failed to retrieve document")
            return None


    @classmethod
    def bulk_insert(cls, documents:List, **kwargs) -> Optional[List[str]] :
        """Persists batch of records into MongoDb. If inserting only one record please use save() function

        Args:
            documents (List): List of records to persist into MongoDb

        Returns:
            Optional[List[str]]: MongoDb Ids of for each record inserted into Db
        """
        collection = _database[cls._get_collection_name()]
        try:
            result = collection.insert_many(
                [doc.to_mongo(**kwargs) for doc in documents]
            )

            return result.inserted_ids
        except errors.WriteError:
            logger.exception("Failed to insert documents")
            return None


    @classmethod
    def _get_collection_name(cls):
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "Document should define an Settings configuration class with the name of the collection"
            )

        return cls.Settings.name

