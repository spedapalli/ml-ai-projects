## Goal :
A simple RAG application that intakes a PDF and lets user query on its contents.

## Tech Stack :
- **qdrant** vector DB
- Tokenization is done using Replicate with Llama
- **OpenAI** as the LLM.
- Python
- Langchain

User uploaded PDF is stored in **qdrant** vector DB. When user queries, the prompt is sent to

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
5. Open PdfIngesterUsingLlamaIndex.py and set the Replicate API token.
6. Create a .env file at the roor and configure add the env variable OPENAI_API_KEY to it along with its value i.e OPENAI_API_KEY=<YOUR KEY>. 
5. #TODO : Ensure all the packages are downloaded and your env is setup
6. Run the cmd `ideation/PdfIngester/src/RAG/Datastore.py`. On the requested input, enter `gen`.
7. Once data is loaded into the DB, query data by running below. You may replace the text "Base pan hole of outdoor unit" with any text in the PDF doc in `data/manuals` folder :
```
ideation/PdfIngester/src/RAG/Query_Data.py "Base pan hole of outdoor unit"
```
8.
