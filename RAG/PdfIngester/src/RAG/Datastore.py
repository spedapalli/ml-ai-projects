# References :
# langchain-qdrant : https://api.python.langchain.com/en/latest/qdrant/langchain_qdrant.qdrant.QdrantVectorStore.html


import os
import getpass
import shutil
from dotenv import load_dotenv
import site
from uuid import uuid4

import openai

from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import qdrant
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']
if not os.environ.get('OPENAI_API_KEY') :
    #
    openai.api_key = getpass.getpass("Enter OpenAI API Key: ")

QDRANT_PATH = "http://localhost:6333"
DATA_PATH = "data/manuals"
COLLECTION_NAME = "manuals"

# -- list of operations
OP_GENERATE_DS = "gen"
OP_QUERY = "query"

def main():
    op = input("Enter operation (gen, query): ")
    if (op == OP_GENERATE_DS):
        generate_datastore()
    elif (op == OP_QUERY) :
        query_str = input("Query: ")
        query_datastore(query_str)
    else :
        print(f"""ERROR: Invalid input.
              Please enter {OP_GENERATE_DS} to upload documents in data/manuals dir OR
              {OP_QUERY} to query previously uploaded data.""")
    # print(site.getsitepackages())


def generate_datastore():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_qdrant(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob='*.pdf')
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(f"Page Content: {document.page_content}")
    print(f"Metadata: {document.metadata}")
    print(f"Document: {type(chunks)}")

    return chunks


def save_to_qdrant(chunks: list[Document]):
    #create a new DB from the documents
    vector_store = create_vector_store()
    ids = [str(uuid4()) for _ in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=ids)



def query_datastore(query_str: str):
    '''
    Queries the Datastore and retrieves matching results with the score for the given string.
    '''
    vector_store = create_vector_store()
    results = vector_store.similarity_search_with_score(query=query_str)
    # print(f"results: {results[0][1]}")
    # for doc, score in results:
    #     # print(f"* {doc.page_content}") # [{doc.metadata}]")
    #     print(f"* [SIM={score:3f}] {doc.page_content} \nMetaData: [{doc.metadata}]")

    return results



def clear_db() :
    # clear out the DB
    if os.path.exists(QDRANT_PATH):
        shutil.rmtree(QDRANT_PATH)



def create_vector_store():
    client = QdrantClient(QDRANT_PATH)

    #-- using lang chain
    if(not(client.collection_exists(COLLECTION_NAME)) ):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    vector_store = QdrantVectorStore(
        client = client,
        collection_name=COLLECTION_NAME,
        embedding=OpenAIEmbeddings(),
    )

    return vector_store


if __name__ == "__main__":
    main()


# #TODO : Below fn is incomplete.
# def save_to_qdrant_1(chunks: list[Document]) :
#     metadata = [
#         {"source":"https://www.shareddocs.com/"}
#     ]

#     client = QdrantClient(QDRANT_PATH)
#     # #TODO : documents param is invalid below. Need to figure the right API call
#     client.add(collection_name=COLLECTION_NAME,
#             documents=chunks,
#             metadata=metadata)

#     qdrant = QdrantVectorStore.from_documents(
#         chunks,
#         embeddings=embeddings,
#         url=QDRANT_PATH,
#         # prefer_grpc=True,
#         collection_name=COLLECTION_NAME
#     )

