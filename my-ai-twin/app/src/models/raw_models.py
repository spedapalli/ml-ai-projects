"""
This module encapsulates classes representing raw data models, pre processing and loading into Vector DB
"""

from typing import Optional

from models.base_models import DataModel


class PostRawModel(DataModel):
    platform: str
    content: dict
    author_id: str | None = None
    image: Optional[str] = None


class ArticleRawModel(DataModel) :
    platform: str
    link: str
    content: dict
    author_id: str


class RepositoryRawModel(DataModel):
    name: str
    link: str
    content: dict
    owner_id: str
