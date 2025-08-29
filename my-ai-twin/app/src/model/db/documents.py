from model.db.base_document import BaseDocument

from pydantic import Field


class UserDocument(BaseDocument):
    """ User specific details """
    first_name: str
    last_name: str

    class Settings:
        name= "users"


class RepositoryDocument(BaseDocument):
    """ Represents document on Github repo  """
    name: str
    link: str
    content: dict
    owner_id: str = Field(alias="owner_id")

    class Settings:
        name= "repositories"


class PostDocument(BaseDocument):
    """ Represents a message post for eg a LinkedIn post """
    platform: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name="posts"


class ArticleDocument(BaseDocument):
    """Represents a published Article such as a post on medium.com

    Args:
        BaseDocument (_type_): _description_
    """
    platform: str
    link: str
    content: dict
    author_id: str = Field(alias="author_id")

    class Settings:
        name = "articles"
