from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

# from featurepipe.featurepipe_config import fp_settings
from core.config import settings


def convert_text_to_embedding(text: str):
    """
    Converts given text into vector embedding using the specified model. By default, uses BAAI/bge-small-en-v1.5 is used.
    But to run on a local machine settings.EMBEDDING_MODEL_MINI_ID can be used.
    """
    model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)
    return model.encode(text)


def convert_repotext_to_embedding(text: str):
    """
    Converts given text into vector embedding using the model 'hkunlp/instructor-xl', specified in core.config.py.
    """
    model = INSTRUCTOR(settings.EMBEDDING_MODEL_FOR_CODE_ID)
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])