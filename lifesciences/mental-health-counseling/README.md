### A tool for Mental Health Counselors

#### Executive summary
A tool for users to gauge a patient's feeling / sentiment based on their statement. 
User may input a patient's feeling in provided UI, and the application returns the corresponding sentiment category.
The chosen model for sentiment analysis is `sid321axn/Bio_ClinicalBERT-finetuned-medicalcondition` given it is already fined tuned on medical condition data. Based on the data used for testing this model categorizes patient's sentiment into below categories : 
- High Blood Pressure
- Depression
- Anxiety
- Pain
- Weight Loss


#### Data Sources
Data used for testing the model is from Kaggle website - https://www.kaggle.com/datasets/thedevastator/nlp-mental-health-conversations/data. It contains primarily 2 fields "Context" and "Response". 

The model is input with "Context", which represents the patient's feelings, and it outputs the Sentiment category along with its confidence in the prediction.


#### Methodology
1. The ask to define a category for a given text is a text classification problem, on unstructured data.
2. Identify if there is an existing pre-trained model for medical condition and the model `sid321axn/Bio_ClinicalBERT-finetuned-medicalcondition` on HuggingFace is found to satisfy this need, to begin with.
3. The data from above datasource is cleansed of NaNs and invalid values, which was one row that had 0 as its value.
4. The input to the model is the "Context" column, which is the patient's description of their feelings.
5. Given we are purely testing a pre-trained model, the necessity to split the dataset into train, test and validate seemed unnecessary.
6. Before the text is input to the model, we lemmitize the words in the text. If the number of words / tokens in the sentence is greater than 512, which is the max tokens supported by the model, we summarize the jist of patient's feelings before running it through the model.
7. The whole exercise was conducted using Jupyter notebook, initially, before putting together a python class to help achieve the objective.
8. APIs were defined and published.
9. A quick and ugly UI was put together as a user interface


#### Results
The model successfully provides the sentiment of patient based on their feelings, along with the confidence score.
![UI Screenshot](images/UIScreenshot.jpg)

**NOTE**: From my testing thus far, the model largely returns -ve feelings, presuming patient is at counseling to get better.

#### Next steps
1. Cleanup docker images and if possible move to podman or other framework.
2. Some visualization charts to that could provide a visual perspective to in and out data
3. Explore other models out there that could potentially do a better job, for eg: feelings can also be positive and current model does not support positive feelings.

#### Outline of project
- Project is built on Python tech stack using its `uv` package manager, `fastapi` for APIs, and `Streamlit` for UI
- ![app](./app/) : folder contains all the backend code including APIs
- ![data](./data/) : When the a link is provided to dowload data from the web, the data is persisted into this local folder. This folder also contains `output` folder that contains CSV files output by the model.
- ![images](./images/) : Images, largely out of the app and in future hopefully charts.
- ![ui](./ui/) : Contains all UI related code
- ![requirements.txt](requirements.txt) : Contains all the dependencies. If using `uv` this file may be used to setup the virtual environment for this project.
- ![pyproject.toml](pyproject.toml) : `uv` package manager config file to track the sources, dependencies, test directory etc..
- ![setup](setup.py) : Script that needs to be run to download some of the needed libraries to format / scale / summarize the text.


#### Running the Application :
- Install `uv` package manager.
- Git clone the project ![mental-health-counseling](.)
- Open terminal. `cd` to the project root folder
- In terminal run `uv pip install -r requirements.txt` : This installs all dependencies listed in requirements.txt
- Run the script `app/setup.py`
- API server : 
    - Start the API server: On terminal, run the command `uvicorn --app-dir ./app api.health_conversation_model_api:app --reload --host 127.0.0.1`
    - By default the server runs on http://localhost:8000
    - To test, go to http://localhost:8000/docs, which takes you to the APIs in OpenApi format, where you can test the one API that is published currently.
    
- UI server : 
    - Start the UI server : On terminal, run the command `streamlit run ui/src/ui.py`, which starts off the server.
    - Above cmd automatically opens a web page (http://localhost:8501) in your default browser
    - Enter text in the text box on the UI page. Click on the button below it. Further below you should see the results, the patient's sentiment prediction as a label, the model's confidence on this prediction and if the text had to be modified the text, further below.

- Dockerize : 
    - In terminal, run the cmd `docker-compose up --build | tee dockercompose.log`. This will kick off both UI and APP servers, with a network bridge between the two.
    - NOTE : The Python script `app/setup.py` is not required. #TODO : This diff between local and dockerize needs to be cleaned up later.

NOTE: Please make sure you do not have conda env or other Python package managers in your default environment PATH since if they precede the PATH before this project's virtual env, they could hijack all the commands and mess up your other environment(s).
