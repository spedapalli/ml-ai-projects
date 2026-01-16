import numpy as np
import umap
from matplotlib import pyplot as plt

# REF : https://medium.com/decodingai/a-real-time-retrieval-system-for-rag-on-social-media-data-9cc01d50a2a0
# https://github.com/decodingai-magazine/articles-code/blob/main/articles/large_language_models/real_time_retrieval_system_for_social_media_data/src/retrievers.py#L89
class RetrievalVisualizer:

    def __init__(self, passages: list[str]) :
        self._passages = passages
        self._umap_transform = self._fit_model(self.passages)
        self._projected_passage_embeddings = self.project_passages(self._passages)


    def _fit_model(self, passages: list[str]) -> umap.UMAP:
        embeddings = np.array(passages)

        _umap_transform = umap.UMAP(random_state=0, transform_seed=0)
        umap_transform = umap_transform.fit(embeddings)

        return umap_transform


    def project_passages(self, passages: list[str]) -> np.ndarray:
        embeddings = np.array(passages)
        return self._project(embeddings = embeddings)


    def _project(self, embeddings: np.ndarray) -> np.ndarray:
        umap_embeddings = np.empty((len(embeddings), 2))

        for i, embeddings in enumerate(embeddings):
            umap_embeddings[i] = self._umap_transform.transform(embeddings)

        return umap_embeddings


    def render(self, embedded_queries: list[list[float]], retrieved_passages: list[str]) -> None:

        assert(self.umap_transform is not None), "Must call `compute_projected_embeddings` first"

        embedded_queries = np.array(embedded_queries)
        projected_query_embeddings = self._project(embedded_queries)

        projected_retrieved_embeddings = self.project_passages(retrieved_passages)

        plt.figure(figsize=(10, 6))
        plt.scatter(self._projected_passage_embeddings[:, 0],
                    self._projected_passage_embeddings[:, 1],
                    s = 10,
                    color='gray',
                    label="All Passages embeddings")

        plt.scatter(projected_query_embeddings[:, 0],
                    projected_query_embeddings[:, 1],
                    s = 100,
                    marker='x',
                    color='k',
                    label='Query Embeddings')

        plt.scatter(
            projected_retrieved_embeddings[:, 0],
            projected_retrieved_embeddings[:, 1],
            s = 100,
            facecolors='none',
            edgecolors='tab:orange',
            label='Retrieved Passages Embeddings'
        )

        plt.gca().set_aspect('equal', adjustable='box')
        plt.axis('off')
        plt.title("Visualization of retrieved passages / embeddings")
        plt.legend()
        plt.show()

