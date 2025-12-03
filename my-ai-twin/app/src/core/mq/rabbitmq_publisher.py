
from core.mq.rabbitmq_connection import RabbitMQConnection
from core.logger_utils import get_logger
from pika import BasicProperties
from pika import exceptions as pikaexceptions
from pika.adapters.blocking_connection import BlockingChannel


logger = get_logger(__file__)
class RabbitMQPublisher:

    def publish_to_rabbitmq(self, queue_name:str, data:str) :
        try:
            rabbitmq_conn = RabbitMQConnection()

            with rabbitmq_conn:
                channel: BlockingChannel = rabbitmq_conn.get_channel()
                # Ensure the queue exists
                channel.queue_declare(queue=queue_name, durable=True)

                channel.confirm_delivery()
                logger.debug(f"Publishing message to RabbitMQ queue: {queue_name}")
                channel.basic_publish(exchange="",
                                      routing_key=queue_name,
                                      body=data,
                                      properties=BasicProperties(delivery_mode=2) # message is persistent
                )
        except pikaexceptions.UnroutableError as e:
            logger.warning("Message could not be routed", e)
        except Exception as e :
            logger.exception("Error publishing to RabbitMQ", e)


if __name__ == "__main__":
    RabbitMQPublisher().publish_to_rabbitmq("datapipe2feature", "Authored by my AI twin")