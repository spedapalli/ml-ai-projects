# project context

## What this is
An AI Twin of myself or anyone who uses this AI Twin
Uses posts to LinkedIn, articles on medium.com and other sites, code repositories on github, to generate corresponding content for the user.
Composes the below layers :
- User inputs a URL or list of URLs to AWS lambda function to initiate processing of published content
- Data collection pipeline processes the input URLs and stores raw data in MongoDB
- A CDC (Change Detection Component) monitors the MongoDB collection and pushes the changes to RabbitMQ
- Feature pipeline runs through sequence of steps using bytewax. It inbounds the message stream from RabbitMQ. Ingests the data, cleans it, chunks it, embeds it and stores it in Qdrant.
- Training pipeline uses the embeddings stored in Qdrant to train a model. The LLM candidate is stored in Model registry, from where it is evaluated and monitored using Opik.
- Inference pipeline is deployed with above LLM model, which in turn intakes users queries and returns responses.

## Stack
- [Python]
- [AWS Lambda]
- [MongoDB]
- [RabbitMQ]
- [Qdrant]
- [Bytewax]
- [Opik]

## Commands
```bash
docker compose -f docker-compose.yml up --build -d
docker-compose up -d --build <service_name>
curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
-d '{"user": "Samba Pedapalli", "link": "https://github.com/spedapalli/ml-ai-projects"}'
{"statusCode": 200, "body": "Link processed successfully"}%
curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
-d '{"user": "Samba Pedapalli", "link": "https://medium.com/@sambas/framework-to-manage-engineering-teams-on-continuous-basis-7c8d05880d6a"}'
pytest -s
```

## Key Directories
- `app/src/` - Application code
- `app/test/` - Unit test code
- `.docker/` - Docker configuration
- `test_scripts/` - Scripts run to speed up testing during local development


## Key Decisions (Dont question these)


## Code Style
- Modularize code as much as possible
- Explicitly declare types for all variables to make code self-documenting
- Tests required for each new feature
- Explicit error handling, no silent catches

## Current Sprint Focus

