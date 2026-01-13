import bytewax.operators as op
from bytewax.dataflow import Dataflow
from datetime import timedelta


# for debug purposes only - comment it out
# import sys
# if len(sys.argv) > 1 and sys.argv[1] == 'local_test':
#     from core.config import settings
#     settings.patch_localhost()

from db.qdrant_connection import QdrantDatabaseConnector
from featurepipe.dataflow.stream_input import RabbitMQSource
from featurepipe.dataflow.stream_output import BytewaxQdrantOutput
from featurepipe.datalogic.dispatchers import (
    ChunkingDispatcher, CleaningDispatcher, EmbeddingDispatcher, RawDispatcher
)

from core.logger_utils import get_logger
logger = get_logger(__name__)

connection = QdrantDatabaseConnector()

logger.info("Successfully started.....................")

flow = Dataflow("Streaming ingestion pipeline")
stream = op.input("input", flow, RabbitMQSource())
logger.info("Reading MQ message.....")
stream = op.map("raw dispatch", stream, RawDispatcher.handle_mq_message)
stream = op.map("clean dispatch", stream, CleaningDispatcher.dispatch_cleaner)

# Batch cleaned data before inserting to Qdrant
# Using collect operator for count-based batching
clean_stream_keyed = op.key_on("cleaned items key", stream, lambda x: "batch_key")
clean_batched = op.collect("batch cleaned data", clean_stream_keyed, timeout=timedelta(seconds=5), max_size=100)

op.output(
    "cleaned data insert to qdrant",
    clean_batched,
    BytewaxQdrantOutput(connection=connection, sink_type="clean"),
)

stream = op.flat_map("chunk dispatch", stream, ChunkingDispatcher.dispatch_chunker)
print("Completed chunking. Moving to embedding.....")
stream = op.map("embedded chunk dispatch", stream, EmbeddingDispatcher.dispatch_embedder)

# Batch embedded data before inserting to Qdrant
vector_stream_keyed = op.key_on("vector items key", stream, lambda x: "batch_key")
vector_batched = op.collect("batch vector data", vector_stream_keyed, timeout=timedelta(seconds=5), max_size=100)

op.output(
    "embedded data insert to qdrant",
    vector_batched,
    BytewaxQdrantOutput(connection=connection, sink_type="vector")
)
