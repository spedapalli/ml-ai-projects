from typing import Self, Optional

import pika
import time
from pika import exceptions as pikaexceptions
from pika.adapters.blocking_connection import BlockingChannel
from core.config import settings
from core.logger_utils import get_logger

logger = get_logger(__file__)

class RabbitMQConnection :
    """
    Singleton class of Rabbit MQ connection
    """

    _instance: Self = None

    def __new__(cls, *args, **kwargs) -> Self :
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    # A good write up on diff btn Connection, Channel and Consumer - https://stackoverflow.com/a/48770082
    # Channel is not thread safe and hence cannot be pooled.
    def __init__(self, host: str | None = None,
                 port: int | None = None,
                 username: str | None = None,
                 password: str | None = None,
                 virtual_host: str = '/',
                 fail_silently: bool = False,
                 **kwargs) -> None :

        self.host = host or settings.RABBITMQ_HOST
        self.port:int = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection: Optional[pika.BlockingConnection] = None


    def __enter__(self) :
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) :
        self.close()


    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        conn_params = pika.ConnectionParameters(
                host=self.host,
                port = self.port,
                virtual_host = self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=2
            )

        # max_retries: int = 5
        # retry_delay = 5
        # for attempt in range (1, max_retries+1) :
        try:
            # Using BlockingConnection (not SelectConnection) since volumes are not expected to be high
            self._connection = pika.BlockingConnection(conn_params)
            logger.info(f"Successfully connected to RabbitMQ at Host: '{self.host}'; Port: '{self.port}'")

        except pikaexceptions.AMQPConnectionError as e:
            # logger.warning(f"Attempt {attempt} : Failed to connect to RabbitMQ at Host: '{self.host}'; Port: '{self.port}'")
            logger.warning(f"Failed to connect to RabbitMQ at Host: '{self.host}'; Port: '{self.port}'")
            logger.exception(e)
            # if attempt < 5 :
            #     logger.info(f"Retrying in {retry_delay} seconds....")
            #     time.sleep(retry_delay)
            # else:
            #     raise ConnectionError(f"Could not connect to RabbitMQ at at Host: '{self.host}'; Port: '{self.port}'"
            #                             f"after {max_retries} attempts") from e

        except Exception as e:
            logger.error(e)
            if not self.fail_silently:
                raise

    def is_connected(self) -> bool :
        return self._connection is not None and self._connection.is_open


    def get_channel(self) -> BlockingChannel :
        if self.is_connected():
            return self._connection.channel()

        return None


    def close(self) :
        if self.is_connected():
            self._connection.close()
            self._connection = None
            logger.info("RabbitMQ connection closed")


