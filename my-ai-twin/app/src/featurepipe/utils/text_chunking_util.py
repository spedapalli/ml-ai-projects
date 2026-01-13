from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

from core.config import settings


def chunk_text(text:str) -> list[str]:
    """Util helps chunk data that is large aka multiple sentences / paragraphs, to be able to generate
    embeddings where input length of str can be a constraint.
    """

    char_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],    # split only paragraphs. Combines paragraphs until the chunk_size is reached
        chunk_size=500,         # max chars to ensure each chunk is less than 500. If
        chunk_overlap=0         #
    )
    text_split = char_splitter.split_text(text=text)
    print("Text split: ", text_split)

    # use the default model "sentence-transformers/all-mpnet-base-v2"
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=50,
        tokens_per_chunk= settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        model_name= settings.EMBEDDING_MODEL_ID
    )

    chunks = []
    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks

