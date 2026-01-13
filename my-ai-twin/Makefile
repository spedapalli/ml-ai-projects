include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

PYTHONPATH := $(shell pwd)/app/src

install: # Create a local Poetry virtual environment and install all required Python dependencies.
	poetry env use 3.11
	poetry install --without superlinked_rag

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ======================================
# ------- Docker Infrastructure --------
# ======================================

local-start: # Build and start your local Docker infrastructure.
	docker compose -f docker-compose.yml up --build -d

local-stop: # Stop your local Docker infrastructure.
	docker compose -f docker-compose.yml down --remove-orphans

# ======================================
# ---------- Crawling Data -------------
# ======================================

local-test-medium: # Make a call to your local AWS Lambda (hosted in Docker) to crawl a Medium article.
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"}'

local-test-github: # Make a call to your local AWS Lambda (hosted in Docker) to crawl a Github repository.
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://github.com/decodingml/llm-twin-course"}'


# ======================================
# -------- RAG Feature Pipeline --------
# ======================================

local-test-retriever: # Test the RAG retriever using your Poetry env
	cd src/feature_pipeline && poetry run python -m retriever

local-generate-instruct-dataset: # Generate the fine-tuning instruct dataset using your Poetry env.
	cd src/feature_pipeline && poetry run python -m generate_dataset.generate


