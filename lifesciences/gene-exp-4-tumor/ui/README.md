### UI for gene-exp-4-tumor

**Author**
Samba Pedapalli


### Outline of project
- src : contains the source of the UI
![src](./src)
![Dependencies](./pyproject.toml)


### Running the Application :
Web app :
    - Open a terminal and `cd` to the directory `gene-exp-4-tumor-ui`. Run the cmd `streamlit run src/ui.py`.
    - Above should automatically open a browser window. If not, type `http://localhost:8501/` in your browser address bar.
    - Upload a CSV file with 18604 columns of gene expressions. In `data` directory there is a test file `xgb_X_after_pca_dataset.csv` you may use.

This is how far you can use the UI before the backend kicks in. Hence, make sure the API server (repo #gene-exp-4-tumor) is up and accessible before you go to the next step. If not, below will result in a Http 500 error.
    - Click on **Predict** button. The table output is in the order in which the records are in the input CSV file.

- To Dockerize the app :
    - Build the docker app, `docker build -t gene-exp-4-tumor-ui .`. For a more detailed output of the build, use `docker build -t gene-exp-4-tumor-ui . --progress=plain --no-cache`.

