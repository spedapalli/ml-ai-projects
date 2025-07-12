
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
import numpy as np
import main

DATA_DIR = './data/'

# app = FastAPI()

client = TestClient(main.app)

def test_api_get():
    response = client.get("/")
    assert response.status_code == 200


def test_api_predict():
    file_path = DATA_DIR + 'xgb_X_after_pca_dataset.csv'

    with open (file_path, 'rb') as file:
        file_content = file.read()

    datafiles = {'file': ('xgb_X_after_pca_dataset.csv', file_content, 'text/csv')}
    response = client.post("/predict", files=datafiles)
    assert response.status_code == 200

    json_response:JSONResponse = response.json()
    prediction = json_response.get('prediction', None)
    # print('Prediction: \n', prediction)
    if prediction is not None:
        prediction_list = list(prediction)
        pred_values = '\n'.join(val for val in prediction_list)
        print(pred_values)
        # for val in prediction_list:
        #     print(f'Predicted value is: {val}')
        # print(f'Predicted value is: {val}' for val in prediction_list)
    else:
        print('No predictions were returned')



    # def test_api_predict(self):
    #     df:DataFrame = pd.read_csv(DATA_ANALYSIS_DIR + 'xgb_X_after_pca_dataset.csv')
    #     unittest_data_df = df.iloc[5:6, 0:]
    #     # convert df to list of dictionaries
    #     records = unittest_data_df.to_dict('records')

    #     # create model instances
    #     model_instances = [IndependentFeatures(**record) for record in records]

    #     main.predict_tumor(model_instances[0])
