import uvicorn
from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
from datamodels.independent_features import IndependentFeatures
from request.independent_features_builder import IndependentFeaturesBuilder


MODELS_DIR = './models/'

app = FastAPI()
# ml_model = joblib.load('./models/XGBoost_model.pkl')
ml_model = joblib.load(f"{MODELS_DIR}xgb_GridSearch_Pipeline.pkl")
print('Loaded model: ', ml_model)

@app.get('/')
def get_data():
    print('Home screen.......')
    return 'test'

@app.post('/predict')
def predict_tumor(indi_features: IndependentFeatures):
    print('Input Req: \n', indi_features.model_dump())
    if (indi_features is None) : return

    # input_req = pd.DataFrame(indi_features.model_dump(), index=[0])
    ind_feature_builder = IndependentFeaturesBuilder()
    input_req = ind_feature_builder.get_all_independent_vars(indi_features.model_dump())
    input_req_df = pd.DataFrame(input_req, index=[0])
    print(input_req_df)
    input_req_df.to_csv('./data-analysis/request.csv')

    prediction = ml_model.predict(input_req_df)
    print("Prediction: ", prediction)
    return {"prediction": int(np.argmax(prediction))}


def main():
    print("Hello from gene-exp-4-tumor!")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
