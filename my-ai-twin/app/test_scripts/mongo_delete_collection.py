# This script is purely for dev purpose when the data in a collection is corrupted
# or not as expected and need to cleanup the collection.

import sys
from pathlib import Path

# Add app/src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import settings
settings.patch_localhost()

from core.logger_utils import get_logger
from db.mongo import MongoDatabaseConnector

logger = get_logger(__name__)

# if execution of this fn results in NotPrimaryError, then update config.py MONGO_DATABASE_HOST
# to point to a different Mongo instance eg: localhost:30003. Try all the 3 mongodb instances
def delete_all_records(collection_name: str):
    mongo = MongoDatabaseConnector()
    db = mongo[settings.MONGO_DATABASE_NAME]
    collection = db[collection_name]
    collection.delete_many({})


if __name__ == "__main__":
    delete_all_records(collection_name="repositories")