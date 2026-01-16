import threading
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

from core.config import settings
from core.logger_utils import get_logger

class ChunkingModelManager:

    _char_splitter_model: Optional[RecursiveCharacterTextSplitter] = None
    _token_splitter_model: Optional[SentenceTransformersTokenTextSplitter] = None
    _lock = threading.Lock()

    @classmethod
    def get_char_splitter_model(cls):
        if cls._char_splitter_model is None:
            with cls._lock:
                if cls._char_splitter_model is None:
                        cls._char_splitter_model = RecursiveCharacterTextSplitter(
                                                        separators=["\n\n"],    # split only paragraphs. Combines paragraphs until the chunk_size is reached
                                                        chunk_size=500,         # max chars to ensure each chunk is less than 500. If
                                                        chunk_overlap=0         #
                        )
        return cls._char_splitter_model



    @classmethod
    def get_token_splitter_model(cls):
        if cls._token_splitter_model is None:
            with cls._lock:
                if cls._token_splitter_model is None:
                    cls._token_splitter_model = SentenceTransformersTokenTextSplitter(
                                                    chunk_overlap=50,
                                                    tokens_per_chunk= settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
                                                    model_name= settings.EMBEDDING_MODEL_ID
                                                )

        return cls._token_splitter_model




