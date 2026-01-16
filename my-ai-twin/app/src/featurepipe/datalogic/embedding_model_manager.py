import threading
from typing import Optional
import torch

from FlagEmbedding import AbsEmbedder, FlagAutoModel
from sentence_transformers.SentenceTransformer import SentenceTransformer

from core.config import settings
from core.logger_utils import get_logger

logger = get_logger(__name__)

class EmbeddingModelManager:
    """ Singleton class to initialize Embedding models only once i.e load once and reused
    """

    # ASSUME : Sentence Transformer
    _text_model: Optional[SentenceTransformer] = None
    # ASSUME : For now assume open source AbsEmbedder aka BGE (BAAI General Embeddings)
    _code_model: Optional[AbsEmbedder] = None
    _lock = threading.Lock()

    @classmethod
    def get_text_model(cls) -> SentenceTransformer:
        if cls._text_model is None:
            with cls._lock:
                if cls._text_model is None:
                    logger.info("Loading text embedding model.....")
                    device_type:str = settings.EMBEDDING_MODEL_GPU_DEVICE if torch.cuda.is_available() else settings.EMBEDDING_MODEL_DEVICE
                    cls._text_model = SentenceTransformer(
                                            settings.EMBEDDING_MODEL_ID,
                                            device=device_type)

        return cls._text_model



    @classmethod
    def get_bge_code_model(cls) -> AbsEmbedder:
        """This is a specific function for code, to use BGE model. Unfortunately it doesnt look like
        these transformers have a common type to use as return type.

        Returns:
            AbsEmbedder: Base class for all BGE (BAAI) models
        """
        if cls._code_model is None:
            with cls._lock:
                if cls._code_model is None:
                    logger.info("Loading BGE Embedding code model")
                    cls._code_model = FlagAutoModel.from_finetuned(
                        settings.EMBEDDING_MODEL_FOR_CODE_ID,
                        use_fp16=True   # Use half precision for 2x speed
                    )
        return cls._code_model



