from typing_extensions import deprecated
from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer
from FlagEmbedding import AbsEmbedder

# from featurepipe.featurepipe_config import fp_settings
from core.config import settings
from core.logger_utils import get_logger
from featurepipe.datalogic.embedding_model_manager import EmbeddingModelManager
import numpy as np

logger = get_logger(__name__)

@deprecated("Please use the batch_encode_text function")
def convert_text_to_embedding(text: str):
    """
    Converts given text into vector embedding using the specified model. By default, uses BAAI/bge-small-en-v1.5 is used.
    But to run on a local machine settings.EMBEDDING_MODEL_MINI_ID can be used.
    Returns :
        Tensor
    """
    model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    return model.encode(text)

@deprecated("Please use the batch_encode_text function")
def convert_repotext_to_embedding(text: str):
    """
    Converts given text into vector embedding using the model 'hkunlp/instructor-xl', specified in core.config.py.
    Returns 768-dimensional vector.
    """
    model = INSTRUCTOR(settings.EMBEDDING_MODEL_FOR_CODE_ID)
    sentence = text
    instruction = "Represent the structure of the repository"
    logger.info(f"Starting encoding of repository text of length {len(sentence)} to Embeddings......")
    # INSTRUCTOR encode expects list of [instruction, text] pairs, returns array
    encoded_text = model.encode([[instruction, sentence]])[0]  # Get first (and only) embedding
    logger.info("Done encoding of repository text to Embedding......")
    return encoded_text


def batch_encode_text(texts: list[str]) -> np.ndarray:
    """Encode multiple texts in a single batch

    Args:
        texts (list[str]): list of texts

    Returns:
        list[np.ndarray]: _description_
    """
    model: SentenceTransformer = EmbeddingModelManager.get_text_model()
    # https://github.com/FlagOpen/FlagEmbedding/blob/master/FlagEmbedding/inference/embedder/encoder_only/base.py
    return model.encode(
            sentences=texts,
            batch_size=32,
            convert_to_numpy=True
            # show_progress_bar=False,
            # normalize_embeddings=True
            )


def batch_encode_code_using_BGE(texts: list[str]) -> np.ndarray :
    model: AbsEmbedder = EmbeddingModelManager.get_bge_code_model()
    # https://github.com/FlagOpen/FlagEmbedding/blob/master/FlagEmbedding/inference/embedder/encoder_only/base.py
    return model.encode(sentences=texts,
                    batch_size=32,
                    convert_to_numpy=True,
                    )


@deprecated("Please use the batch_encode_code_using_BGE function")
def convert_repotext_to_embedding_BGE(model:AbsEmbedder, text: str):
    """This fn intakes the model itself to optimize on how the model is loaded and initialized from HuggingFace

    Args:
        model (AbsEmbedder): Class as defined in https://github.com/FlagOpen/FlagEmbedding/blob/6fd176266f2382878bcc69cd656cff425d52f49b/FlagEmbedding/abc/inference/AbsEmbedder.py
        text (str): _description_
    """
    return _convert_repotext_to_embedding_(model, text)

@deprecated("Please use the batch_encode_code_using_BGE function")
def _convert_repotext_to_embedding_(model, text: str):

    sentence = text
    instruction = "Represent the structure of the repository"
    logger.info(f"Starting encoding of repository text of length {len(sentence)} to Embeddings using Model id= {id(model)}......")
    # INSTRUCTOR encode expects list of [instruction, text] pairs, returns array
    encoded_text = model.encode([[instruction, sentence]])[0]  # Get first (and only) embedding
    logger.info("Done encoding of repository text to Embedding......")
    return encoded_text

