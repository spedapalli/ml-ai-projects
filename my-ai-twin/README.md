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
- QDrant (http://localhost:6333/dashboard#) used for :
-- As a "clean data sink" for documents, before storing in vector db
-- Storing the vector representation of the above documents.
-- Ports : 6333 (Http), 6334 (gRPC). 6335 is also exposed but here we do not have a distributed deployment of qdrant and hence not used.

MQ :
- RabbitMQ (http://localhost:15672/) :
-- Port : 5673 for communications and 15673 for management console access

#### Running the Application :
##### Test Data Crawlers :
1. `cd` into the directory. Run `docker compose -f docker-compose.yml up --build -d`. If you want to only build data-crawlers module, please see the `docker-compose.yml` file as of this commit. *NOTE* : Crawlers is the only module configured to use x86_amd64 architecture given Google provides chrome browser
for this architecture by default. Installing chromium for arm64 architecture on Amazon Linux 2023 version proved out to be lot more challenging.
2. Run this cmd to test `curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
-d '{"user": "Samba Pedapalli", "link": "https://medium.com/@sambas/framework-to-manage-engineering-teams-on-continuous-basis-7c8d05880d6a"}'`
3. Run the cmd to test Github URL : `curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Samba Pedapalli", "link": "https://github.com/spedapalli/ml-ai-projects/tree/my-ai-twin-1/my-ai-twin"}'`
4. **Debugging** : To debug the crawler code, given it uses AWS Lambda (RIE), it involves few steps as detailed further below and here is a high level flow.
Lambda starts -> Handler imports -> debugpy.listen() (in the handler class) opens port 5678 -> Code continues normal execution -> Attach debugger in VS Code
Steps :
	a. Refer to launch.json and its config with debugpy
	b. Make sure you install debugpy in your environment
	c. In .docker/Dockerfile.data_crawlers, uncomment out below lines :
	```
	ENV AWS_LAMBDA_SIMULATOR_LOC=/usr/local/bin
	RUN mkdir -p ${AWS_LAMBDA_SIMULATOR_LOC} && curl -Lo ${AWS_LAMBDA_SIMULATOR_LOC}/aws-lambda-rie \
	https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie \
	&& chmod +x ${AWS_LAMBDA_SIMULATOR_LOC}/aws-lambda-rie
```
	d. In docker-compose.yml, under `data-crawlers:` config, uncomment out below lines :
	```
	entrypoint: ["/usr/local/bin/aws-lambda-rie"]
    command: ["/var/lang/bin/python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "awslambdaric", "datapipe.aws_lambda_handler.handler"] # for debug only. Comment out for prod deployment
	```
	f. Set breakpoints in the code.
	g. Build the docker container using `docker compose -f docker-compose.yml up --build -d` or in case of changes to data-crawlers which is the entry point - `docker-compose build data-crawlers`.
	h. Run the CURL command to trigger AWS Lambda function. `curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
		-d '{"user": "Samba Pedapalli", "link": "https://medium.com/@sambas/framework-to-manage-engineering-teams-on-continuous-basis-7c8d05880d6a"}'`
	i. Attach VS code debugger using "Python Debugger : Debug Python file". If this is not configured, make sure to config launch.json.
	j.

##### Test CDC :
1. Build the docker containers using the same command as above in [Test Data Crawlers](#test-data-crawlers-)
2. Execute the CURL command in above [Test Data Crawlers](#test-data-crawlers-)

##### Unit Test Feature pipeline :
1. `cd` into the directory. Switch to the local python environment by running `source .venv/bin/activate`.
2. In your docker console, make sure all the 3 mongodb instances are running and active. NOTE Unit tests are currently designed to run against localhost
3. Run `pytest` to run all the unit tests.
4. To run a single test run `pytest <test file path>` eg: `pytest app/test/featurepipe/dataset_generator_test.py`

There are few files in the `src` directory with `main` function and if you need to run these for any reason, follow the process below which demonstrates the process to run `retriever_localtest.py`:
1. `cd app/src/featurepipe`, which is where a test file exists to run and test RAG. Run `poetry run python -m retriever_localtest`
2. To debug, in VS Code open `my-ai-twin/app/src/featurepipe/retriever_localtest.py`. Go to Run / Debug and click on "Python Debugger : Debug Python file"


##### Contact and Further Information


### Work In Progress :
[8 Jan 2026] : Testing with Git repo. Data gets written to cleaned_repositories in QDrant but the embeddings do not get written to vector_repositories. In feature-pipe docker pod, the log shows below message, which indicates the embeddings werent created and unsure if it is taking too long given the large files :