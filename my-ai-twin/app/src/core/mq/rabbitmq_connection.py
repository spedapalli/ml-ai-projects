from typing import Self

import pika
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
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_DEFAULT_USERNAME
        self.password = password or settings.RABBITMQ_DEFAULT_PASSWORD
        self.virtual_host = virtual_host
        self.fail_silently = fail_silently
        self._connection: pika.BlockingConnection = None


    def __enter__(self) :
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) :
        self.close()


    def connect(self):
        try:
            print("in MQ init :Host ", self.host)
            print("in MQ init :Port ", self.port)
            print(f"in MQ init :username '{self.username}'")
            print(f"in MQ init :password '{self.password}'")

            credentials = pika.PlainCredentials(self.username, self.password)
            print("in MQ init :Virtual Host ", self.virtual_host)
            # Using BlockingConnection (not SelectConnection) since volumes are not expected to be high
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port = self.port,
                    virtual_host = self.virtual_host,
                    credentials=credentials,
                )
            )
        except pikaexceptions.AMQPConnectionError as e:
            logger.warning(f"Failed to connect to RabbitMQ at Host: '{self.host}'; Port: '{self.port}'")
            logger.exception(e)
            if not self.fail_silently:
                raise e

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


