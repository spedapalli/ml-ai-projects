import configparser
from io import BytesIO
from utils.AwsS3FileUtil import read_file
import joblib


class ModelsReader:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('resources/config.ini')

        self.aws_bucket = config['AWS_S3_Model_Storage']['BUCKET']
        self.aws_xgb_model = config['AWS_S3_Model_Storage']['XGB_MODEL_FILE']
        self.xgb_model = None



    def get_xgb_model(self):
        if not self.xgb_model:
            xgb_model_bytes:BytesIO = read_file(self.aws_bucket, self.aws_xgb_model)
            self.xgb_model = joblib.load(xgb_model_bytes)
            if self.xgb_model is not None:
                print(f"Successfully loaded {self.aws_xgb_model} from AWS S3")

        return self.xgb_model

