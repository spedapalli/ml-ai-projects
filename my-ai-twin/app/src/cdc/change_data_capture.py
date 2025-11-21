import json

from bson import json_util
from pymongo.change_stream import DatabaseChangeStream

from db.mongo import MongoDatabaseConnector
from core.config import settings
from featurepipe.featurepipe_config import fp_settings
from core.logger_utils import get_logger
from core.mq.rabbitmq_publisher import RabbitMQPublisher


logger = get_logger(__file__)

class ChangeDataCapturer:

    def stream_process(self):
        try :
            client = MongoDatabaseConnector()
            db = client[settings.MONGO_DATABASE_NAME]
            logger.info(f"Connected to MongoDB. Database name: {settings.MONGO_DATABASE_NAME}")

            # watch for changes in a specific collection -  all places where 'operationType' has 'insert' value
            # mongo db query: {"op": { "$in": ["i"] }, "ns": "twin.articles" }
            # changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])
            pipeline = [{"$match": {"operationType": "insert"}}]
            changes: DatabaseChangeStream = db.watch(pipeline, full_document='updateLookup')

            for change in changes:
                data_type = change["ns"]["col"]
                entry_id = str(change["full_document"]["_id"])  # convert Db Object id to string

                change["full_document"].pop("_id")
                change["full_document"]["type"] = data_type
                change["full_document"]["entry_id"] = entry_id

                # for now only below 3. ignore users and other collections
                if data_type not in ["articles", "posts", "repositories"]:
                    logger.info(f"Unsupported data type: {data_type}")
                    continue

                # serialize non-json serializable objs (eg: binary) using json_util
                data = json.dumps(change["full_document"], default=json_util.default)
                logger.debug(f"Change detected and serialized for a data sample of type {data_type}")

                # publish to RabbitMQ
                RabbitMQPublisher().publish_to_rabbitmq(queue_name=fp_settings.RABBITMQ_QUEUE_NAME, data=data)
                logger.info(f"Data of type {data_type} published to RabbitMQ.")

        except Exception as err:
            logger.error(f"An error occurred: {err}")


if __name__ == "__main__":
    ChangeDataCapturer().stream_process()