from io import BytesIO
import pandas as pd
import numpy as np

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from src.datamodels.independent_features import IndependentFeatures
from request.independent_features_builder import IndependentFeaturesBuilder
from adapters.ModelsReader import ModelsReader
from utils.AppConfigParser import AppConfigParser
from utils.SecretsLoader import SecretsLoader


LOCAL_MODELS_DIR = './models/'
## 0=BRCA 1=COAD, 2=KIRC, 3=LUAD, 4=PRAD
TARGET_VAR_MAP = {0: 'BRCA', 1: 'COAD', 2: 'KIRC', 3: 'LUAD', 4: 'PRAD'}

# --- init config classes
# parse the config
config_parser = AppConfigParser()
secrets_loader = SecretsLoader(config_parser.secrets_file_loc)
model_reader = ModelsReader(config_parser, secrets_loader)

app = FastAPI()

@app.get('/')
def home():
    print('Home screen.......')
    return 'test'


@app.post('/predict')
async def predict_xgb(file: UploadFile = File(...)) -> JSONResponse:
    '''
    @param file : CSV file containing the 18604 gene expressions
    '''
    content = await file.read()

    gene_df = pd.read_csv(BytesIO(content), index_col=0)

    ml_model = model_reader.get_xgb_model()
    prediction = ml_model.predict(gene_df)

    result = [TARGET_VAR_MAP[int(np.argmax(arr_ele))] for arr_ele in prediction]
    # print(result)
    # print(int(np.argmax(prediction[0])))
    # return result
    return JSONResponse(content={"prediction" : result})



# Deprecated
# @DeprecationWarning('Random generation is not a good approach. Hence deprecating.')
@app.post('/predict-tumor')
def predict_tumor(indi_features: IndependentFeatures):
    '''
    For vars not provided, random numbers are generated based on statistical values of each var
    '''
    print('Input Req: \n', indi_features.model_dump())
    if (indi_features is None) : return

    # input_req = pd.DataFrame(indi_features.model_dump(), index=[0])
    ind_feature_builder = IndependentFeaturesBuilder()
    input_req = ind_feature_builder.get_all_independent_vars(indi_features.model_dump())
    input_req_df = pd.DataFrame(input_req, index=[0])
    # print(input_req_df)
    # input_req_df.to_csv('./data-analysis/request.csv')

    ml_model = model_reader.get_xgb_model()

    prediction = ml_model.predict(input_req_df)
    print("Prediction: ", prediction)
    return {"prediction": int(np.argmax(prediction))}


def main():
    print("Hello from gene-exp-4-tumor!")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
