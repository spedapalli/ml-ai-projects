import sys
from pathlib import Path

# For testing (or learning) purpose only, not PROD :
# To test this aka usage of featurepipe along with core module, add ./src dir to PYTHONPATH.
#
from dotenv import load_dotenv

# ROOT_DIR = str(Path(__file__).parents[2] / "src")
# sys.path.append(ROOT_DIR)
load_dotenv()   # load the env vars for test

from core import logger_utils
from core.config import settings
# IMPORTANT : Initialize to use mongodb on localhost before any module using MongoDB is imported
# TODO : TO run this in CICD pipeline will need to figure out where mongodb wud run and how to access it
settings.patch_localhost()

from core.rag.vector_retriever import VectorRetriever

logger = logger_utils.get_logger(__name__)


def test_retriever():

    query = """
        Hello I am Samba Pedapalli.
        Could you draft an article paragraph discussing RAG ? I am particularly interested in how to design a RAG system.
        """

    retriever = VectorRetriever(query=query)
    hits = retriever.retrieve_top_k(k= 6, to_expand_to_n_queries=5)
    reranked_hits = retriever.rerank(hits=hits, keep_top_k=5)

    logger.info("======== Retreived Documents =========")
    for rank, hit in enumerate(reranked_hits):
        logger.info(f"Rank = {rank} : {hit}")