from abc import ABC, abstractmethod

from pydantic import BaseModel


class DataModel(BaseModel):
    """
    Abstract class for all data models
    """

    entry_id:str
    type:str


class VectorDBDataModel(ABC, DataModel):
    """Abstract class for all Vector DB based data models

    Args:
        ABC (_type_): _description_
        DataModel (_type_): _description_
    """

    @abstractmethod
    def to_payload(self) -> tuple :
        pass
