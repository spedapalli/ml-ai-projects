# REF : https://pypi.org/project/llama-index/
# REF : https://github.com/run-llama/llama_index
## ------ Future work in progress -------

import os
os.environ["REPLICATE_API_TOKEN"] = <YOUR_REPLICATE_TOKEN>

from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.replicate import Replicate
from llama_index.readers.qdrant import QdrantReader
from transformers import AutoTokenizer

DOCS_DIR = "data/manuals"

# set the LLM
llama2_7b_chat = "meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e"
Settings.llm = Replicate(
    model=llama2_7b_chat,
    temperature=0.01,
    additional_kwargs={"top_p": 1, "max_new_tokens": 300},
)

# set tokenizer to match LLM
Settings.tokenizer = AutoTokenizer.from_pretrained(
    "NousResearch/Llama-2-7b-chat-hf"
)

# set the embed model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

documents = SimpleDirectoryReader(input_files=[f'{DOCS_DIR}/IM-38MURA-02.pdf']).load_data()
print(f'document size: {len(documents)}')
# store the doc as a vector
index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine()
# --- query Carfax report
# print(query_engine.query("What make is the car ?"))
# print(query_engine.query("How many accidents does it have ?"))
# print(query_engine.query("What is the MSRP for the car ?"))

# --- query Heat pump doc
print(query_engine.query("What model is the pump ?"))
print(query_engine.query("Is it an indoor or outdoor unit ?"))

#TODO : Use local Vector DB (Qdrant) instead of remote / inbuilt vector DB.
# REF : https://docs.llamaindex.ai/en/stable/examples/data_connectors/QdrantDemo/