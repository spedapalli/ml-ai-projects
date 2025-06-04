# from unittest import TestCase
# from fastapi import FastAPI

from fastapi.testclient import TestClient

# import pandas as pd
# from pandas import DataFrame
import main
# from datamodels.independent_features import IndependentFeatures

DATA_ANALYSIS_DIR = './data-analysis'

# app = FastAPI()

client = TestClient(main.app)

def test_api_predict():
    response = client.get("/")
    assert response.status_code == 200

    # def test_api_predict(self):
    #     df:DataFrame = pd.read_csv(DATA_ANALYSIS_DIR + 'xgb_X_after_pca_dataset.csv')
    #     unittest_data_df = df.iloc[5:6, 0:]
    #     # convert df to list of dictionaries
    #     records = unittest_data_df.to_dict('records')

    #     # create model instances
    #     model_instances = [IndependentFeatures(**record) for record in records]

    #     main.predict_tumor(model_instances[0])
