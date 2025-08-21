## Goal :
A simple RAG application that intakes a PDF and lets user query on its contents.

## Tech Stack :
- **qdrant** vector DB
- Langchain libraries / interfaces to Qdrant, OpenAI Embeddings, Prompt template etc..
- **OpenAI** Embeddings : default "text-embedding-ada-002" model for embeddings and  as the LLM.
- Python

Flow : 
1. User uploads the PDF docs into vector DB **qdrant**
2. User queries for a datapoint in the PDF, at which point :
    a. User query is looked up in the Datastore
    b. To the above result, a predefined prompt template is prefixed to provide context on what is being asked from the LLM
    c. LLM formats the result from above datastore into proper english sentence.


## Setup :
1. Install Docker
2. Install qdrant as a docker container. You may refer to https://qdrant.tech/documentation/quickstart/
`docker pull qdrant/qdrant`
3. Run the qdrant instance. Note, the port is currently hardcoded to 6333
```
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```
4. Install `uv` Python packager, preferrably to speed up setting up your environment.
4. Git pull code from this repo
5. Create a .env file at the root and configure add the env variable OPENAI_API_KEY to it along with its value i.e OPENAI_API_KEY=<YOUR KEY>. 
6. #TODO : Ensure all the packages are downloaded and your env is setup
7. Run the cmd `ideation/PdfIngester/src/RAG/Datastore.py`. On the requested input, enter `gen`.
8. Once data is loaded into the DB, query data by running below. You may replace the text "Base pan hole of outdoor unit" with any text in the PDF doc in `data/manuals` folder :
```
ideation/PdfIngester/src/RAG/Query_Data.py "Base pan hole of outdoor unit"
```
8.
