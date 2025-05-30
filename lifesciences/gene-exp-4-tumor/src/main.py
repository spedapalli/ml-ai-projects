from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
from datamodels.Independent_Features import Independent_Features


app = FastAPI()
ml_model = joblib.load('./models/XGBoost_model.pkl')
print('Loaded model: ', ml_model)

@app.get('/')
def get_data():
    return 'test'

@app.post('/predict')
def predict_tumor(indi_features: Independent_Features):
    print(indi_features.model_dump())

    # input_req = pd.DataFrame(indi_features.model_dump(), index=[0])
    input_req = {f'pca{i}':0 for i in range(0, 640)}
    input_req_df = pd.DataFrame(input_req, index=[0])
    print(input_req_df)

    prediction = ml_model.predict(input_req_df)
    print("Prediction: ", prediction)
    return {"prediction": int(np.argmax(prediction))}


def main():
    print("Hello from gene-exp-4-tumor!")


if __name__ == "__main__":
    main()
