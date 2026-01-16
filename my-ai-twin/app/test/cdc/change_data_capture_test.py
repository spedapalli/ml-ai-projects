import pytest

# IMPORTANT : Initialize to use mongodb on localhost before any module is imported. Else it defaults to docker instance
# TODO : TO run this in CICD pipeline will need to figure out where mongodb wud run and how to access it
from core.config import settings
settings.patch_localhost()

from cdc import change_data_capture

from pymongo import MongoClient

def test_insert_data_to_mongodb(uri="mongodb://localhost:30001/?directConnection=true",
                                db_name:str='twin',
                                collection_name:str = 'posts',
                                data: dict = {"platform": "LinkedIn", "content": "Test content"}):
    """Test inserting of data into mongo db for a given collection

    Args:
        uri (_type_): MongoDB URI
        dbname (_type_): Name of the database eg: twin
        collection_name (_type_): Name of the collection eg: users
        data (_type_): Data to be inserted (dict)
    """
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    try:
        result = collection.insert_one(data)
        print(f"Data inserted with _id: {result.inserted_id}")
    except Exception as e:
        print (f"An error occurred: {e}")
    finally:
        client.close()


