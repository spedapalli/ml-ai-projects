import sys
from pathlib import Path

# For testing (or learning) purpose only, not PROD :
# To test this aka usage of featurepipe along with core module, add ./src dir to PYTHONPATH.
#
from dotenv import load_dotenv

ROOT_DIR = str(Path(__file__).parents[2] / "src")
sys.path.append(ROOT_DIR)
load_dotenv()   # load the env vars for test

from core import logger_utils
from core.config import settings

# Patch localhost settings BEFORE importing modules that initialize DB connections
# Critical for test to succeed
settings.patch_localhost()

from core.rag.vector_retriever import VectorRetriever

logger = logger_utils.get_logger(__name__)

# INSTRUCTION to run the test. cd into app/src/featurepipe and run `poetry run python -m retriever_localtest``
if __name__ == "__main__":
    query = """
        Hello I am Samba Pedapalli.
        Could you draft an article paragraph discussing RAG ? I am particularly interested in how to design a RAG system.
        """

    # to test locally
    # to test locally
    # settings.patch_localhost() # Moved to top level

    retriever = VectorRetriever(query=query)
    hits = retriever.retrieve_top_k(k= 6, to_expand_to_n_queries=5)
    reranked_hits = retriever.rerank(hits=hits, keep_top_k=5)

    logger.info("======== Retreived Documents =========")
    for rank, hit in enumerate(reranked_hits):
        logger.info(f"Rank = {rank} : {hit}")

