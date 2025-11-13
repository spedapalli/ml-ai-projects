from InstructorEmbedding import INSTRUCTOR
from sentence_transformers.SentenceTransformer import SentenceTransformer

from featurepipe.featurepipe_config import fp_settings


def convert_text_to_embedding(text: str):
    model = SentenceTransformer(fp_settings.EMBEDDING_MODEL_ID)
    return model.encode(text)


def convert_repotext_to_embedding(text: str):
    model = INSTRUCTOR("hkunlp/instructor-xl")
    sentence = text
    instruction = "Represent the structure of the repository"
    return model.encode([instruction, sentence])