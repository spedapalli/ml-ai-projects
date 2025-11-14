import json
import time
from datetime import datetime
from typing import Generic, Iterable, List, Optional, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition
from featurepipe.featurepipe_config import fp_settings
from core import logger_utils
from core.mq.rabbitmq_connection import RabbitMQConnection


logger = logger_utils.get_logger(__name__)

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")


class RabbitMQPartition (StatefulSourcePartition, Generic[DataT, MessageT]):
    """
    Creates connection between Bytewax and RabbitMQ, to transfer data from MQ to Bytewax streaming pipeline.
    By inheriting StatefullSourcePartition, enables snapshot functionality to save the state of the queue.
    """

    # A good writeup on MQ Connection, Channel and Consumer difference - https://stackoverflow.com/a/48770082
    def __init__(self, queue_name:str, resume_state:MessageT | None = None) -> None:
        self._in_flight_msg_ids: MessageT = resume_state or set()
        self.queue_name = queue_name
        self.connection = RabbitMQConnection()
        self.connection.connect()
        self.channel = self.connection.get_channel()

    # def next_batch(self, sched: Optional[datetime]) -> Iterable[DataT] :
    def next_batch(self) -> Iterable[DataT] :
        try:
            method_frame, header_frame, body_frame = self.channel.basic_get(
                queue=self.queue_name,
                auto_ack=True)
        except Exception as e :
            logger.error(f"Error while fetching message from Queue={self.queue_name}")
            time.sleep(10)  #TODO - replace this hack with more elegant solution aka wait for connection before exec this operation

            self.connection.connect()
            self.channel = self.connection.get_channel()
            return []

        if method_frame:
            msg_id = method_frame.delivery_tag
            self._in_flight_msg_ids.add(msg_id)

            return [json.loads(body_frame)]
        else:
            return []

    def snapshot(self) -> MessageT:
        return self._in_flight_msg_ids

    def garbage_collect(self, state):
        closed_in_flight_msg_ids = state
        for msg_id in closed_in_flight_msg_ids:
            self.channel.basic_ack(delivery_tag=msg_id)
            self._in_flight_msg_ids.remove(msg_id)


    def close(self):
        self.channel.close()



class RabbitMQSource(FixedPartitionedSource):
    def list_parts(self) -> List[str] :
        return ["single partition"]

    def build_part(self,
                   now:datetime,
                   for_part: str,
                   resume_state: MessageT | None = None) -> StatefulSourcePartition[DataT, MessageT]:

        return RabbitMQPartition(queue_name=fp_settings.RABBITMQ_QUEUE_NAME)



