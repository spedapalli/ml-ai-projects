import pytest
from featurepipe.utils import text_chunking_util

def test_chunk_data():
    long_txt = """This is a long document with multiple paragraphs. This is purely used to test sentence transformer algorithms
    that are used to split long text into smaller chunks.

    This is the second paragraph, and it also contains several sentences. The small chunks of text are then fed to an embedding
    model to create embeddings which is then written to a vector db for storage. The vector db helps us identify the exact match
    or the closest match to a user query, quering our system. What happens if I add more text here ???

    The PytestConfigWarning: Unknown config option: asyncio_mode warning indicates that Pytest does not recognize the asyncio_mode
     option specified in your pytest.ini file or other Pytest configuration. This typically happens when the pytest-asyncio
     plugin, which provides this option, is not installed or not correctly recognized by your Pytest environment.

    Finally, here's a third paragraph for demonstration."""

    chunked_text: list[str] = text_chunking_util.chunk_text(long_txt)
    for i, txt in enumerate(chunked_text) :
        print(f"Data chunk at index {i} is {txt}")