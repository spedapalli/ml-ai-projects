import concurrent.futures

import opik
from core.config import settings
from qdrant_client import models
from sentence_transformers.SentenceTransformer import SentenceTransformer

from core.logger_utils import get_logger
from core import string_utils
from db.qdrant_connection import QdrantDatabaseConnector
from core.rag.query_expansion import QueryExpansion
from core.rag.reranker import ReRanker
from core.rag.self_query import SelfQuery


logger = get_logger(__name__)

class VectorRetriever:
    """Retrieves Vectors from a Vector store using query expansion and multitenancy search.
    """

    def __init__(self, query: str) -> None:
        self._client = QdrantDatabaseConnector()
        self.query = query
        self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
        self._query_expander = QueryExpansion()
        self._metadata_extractor = SelfQuery()
        self._reranker = ReRanker()


    def _search_single_query(self, generated_query: str, author_id: str, k: int):
        assert k > 3, "k should be greater than 3"

        query_vector = self._embedder.encode(generated_query).tolist()
        vectors = [
            self._client.search(
                collection_name="vector_posts",
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=author_id,
                            match=models.MatchValue(value=author_id),
                        )
                    ]
                    if author_id
                    else None
                ),
                query_vector = query_vector,
                limit=k // 3,
            ),
            self._client.search(
                collection_name="vector_articles",
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=author_id,
                            match=models.MatchValue(value=author_id),
                        )
                    ]
                    if author_id
                    else None
                ),
                query_vector = query_vector,
                limit = k // 3,
            ),
            self._client.search(
                collection_name="vector_repositories",
                query_filter= models.Filter(
                    must=[
                        models.FieldCondition(
                            key= "owner_id",
                            match= models.MatchValue(value=author_id),
                        )
                    ]
                    if author_id
                    else None
                ),
                query_vector = query_vector,
                limit = k // 3,
            ),
        ]
        return string_utils.flatten_nested_list(vectors)


    @opik.track(name="retriever.retrieve_top_k")
    def retrieve_top_k(self, k: int, to_expand_to_n_queries:int) -> list:
        generated_queries = self._query_expander.generate_response(
            self.query, to_expand_to_n=to_expand_to_n_queries
        )
        logger.info("Successfully generated queries for search: ", num_queries = len(generated_queries))

        author_id = self._metadata_extractor.generate_response(self.query)
        if author_id:
            logger.info("Successfully extracted the author_id from the query: ", author_id = author_id)
        else :
            logger.warn("Unable to find any Author data in the user's prompt")


        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [
                executor.submit(self._search_single_query, query, author_id, k)
                for query in generated_queries
            ]

            hits = [
                task.result() for task in concurrent.futures.as_completed(search_tasks)
            ]
            hits = string_utils.flatten_nested_list(hits)

        logger.info("All documents retrieved successfully: ", num_documents=len(hits))

        return hits



    @opik.track(name="retriever.rerank")
    def rerank(self, hits: list, keep_top_k: int) -> list[str]:
        content_list = [hit.payload["content"] for hit in hits]
        rerank_hits = self._reranker.generate_response(
            query=self.query, passages=content_list, keep_top_k=keep_top_k
        )

        logger.info("Documents reranked successfully: ", num_documents=len(rerank_hits))
        return rerank_hits


    def set_query(self, query: str):
        self.query = query

