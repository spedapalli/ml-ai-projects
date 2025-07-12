from io import BytesIO
import joblib

from utils.AwsS3FileUtil import AwsS3FileUtil
from utils.AppConfigParser import AppConfigParser
from utils.SecretsLoader import SecretsLoader

class ModelsReader:

    def __init__(self, config_parser:AppConfigParser, secrets_loader: SecretsLoader):
        self.config_parser = config_parser
        self.secrets_loader = secrets_loader
        self.xgb_model = None



    def get_xgb_model(self):
        if not self.xgb_model:
            aws_util: AwsS3FileUtil = AwsS3FileUtil(self.config_parser, self.secrets_loader)
            xgb_model_bytes:BytesIO = aws_util.read_file(bucket_name=self.config_parser.aws_bucket,
                                                              s3_key=self.config_parser.aws_xgb_model_file)

            self.xgb_model = joblib.load(xgb_model_bytes)
            if self.xgb_model is not None:
                print(f"Successfully loaded {self.config_parser.aws_xgb_model_file} from AWS S3")

        return self.xgb_model

