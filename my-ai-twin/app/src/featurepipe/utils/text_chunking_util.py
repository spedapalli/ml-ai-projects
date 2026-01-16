from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

from core.config import settings
from featurepipe.datalogic.chunking_model_manager import ChunkingModelManager


def chunk_text(text:str) -> list[str]:
    """Util helps chunk data that is large aka multiple sentences / paragraphs, to be able to generate
    embeddings where input length of str can be a constraint.
    """
    # Keeping sentences and para intact, split across paragraphs
    # char_splitter = RecursiveCharacterTextSplitter(
    #     separators=["\n\n"],    # split only paragraphs. Combines paragraphs until the chunk_size is reached
    #     chunk_size=500,         # max chars to ensure each chunk is less than 500. If
    #     chunk_overlap=0         #
    # )
    char_splitter = ChunkingModelManager.get_char_splitter_model()
    text_split = char_splitter.split_text(text=text)
    print("Text split: ", text_split)

    # Split abv text into tokens (words/subwords).Use the default model "sentence-transformers/all-mpnet-base-v2"
    # token_splitter = SentenceTransformersTokenTextSplitter(
    #     chunk_overlap=50,
    #     tokens_per_chunk= settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
    #     model_name= settings.EMBEDDING_MODEL_ID
    # )

    token_splitter = ChunkingModelManager.get_token_splitter_model()
    chunks = []
    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks

