#### Executive summary
A project more focused on MLOps than model training. The goal is for the model to consume a users's published data on the web and generate text that resembles the style of this user.
The project is inspired and modeled based on https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f. Code is adapted to my coding style and understanding.

##### Findings :


#### Rationale


#### Research Question
The relation between tumors and Gene expressions to 5 types of cancers.

#### Data Sources
- LinkedIn
- GitHub
- Medium
- Other sources can be embedded such as substack etc..

#### Methodology


#### Results



#### Next steps


#### Outline of project

Database :
- MongoDB is used given the data from crawler is a document, not relational data.
-- Ports : 3000x (non-standard) used
-- Redundency is implemented using 3 replicas to make sure if 1 primary goes down, there is always a secondary in place.
- QDrant used for :
-- As a "clean data sink" for documents, before storing in vector db
-- Storing the vector representation of the above documents.
-- Ports : 6333 (Http), 6334 (gRPC). 6335 is also exposed but here we do not have a distributed deployment of qdrant and hence not used.

MQ :
- RabbitMQ :
-- Port : 5673 for communications and 15673 for management console access

#### Running the Application :
##### Test Data Crawlers :
1. `cd` into the directory. Run `docker compose -f docker-compose.yml up --build -d`. If you want to only build data-crawlers module, please see the `docker-compose.yml` file as of this commit. *NOTE* : Crawlers is the only module configured to use x86_amd64 architecture given Google provides chrome browser
for this architecture by default. Installing chromium for arm64 architecture on Amazon Linux 2023 version proved out to be lot more challenging.
2. Run this cmd to test `curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
-d '{"user": "Samba Pedapalli", "link": "https://medium.com/@sambas/framework-to-manage-engineering-teams-on-continuous-basis-7c8d05880d6a"}'`
3. Run the cmd to test Github URL : `curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Samba Pedapalli", "link": "https://github.com/spedapalli/ml-ai-projects/tree/my-ai-twin-1/my-ai-twin"}'`

##### Test Feature pipeline :
1. `cd` into the directory. Switch to the local python environment by running `source .venv/bin/activate`.
2. In your docker console, make sure all the 3 mongodb instances are running and active.
2. Run `poetry run python -m retriever`
3. To debug, in VS Code open `my-ai-twin/app/src/featurepipe/retriever.py`. Go to Run / Debug and click on "Python Debugger : Debug Python file"

##### Contact and Further Information
