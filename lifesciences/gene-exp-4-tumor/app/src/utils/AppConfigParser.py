
import configparser
import os

class AppConfigParser:

    def __init__(self):
        config = configparser.ConfigParser()
        if os.path.exists('resources/config.ini'):
            with open('resources/config.ini', 'r') as configfile:
                config.read_file(configfile)

                config.read('resources/config.ini')
                self.aws_bucket = config['AWS_S3_Model_Storage']['BUCKET']
                self.aws_xgb_model_file = config['AWS_S3_Model_Storage']['XGB_MODEL_FILE']
                self.aws_default_region = config['AWS_CONFIG']['AWS_DEFAULT_REGION']
                self.secrets_file_loc = config['SECRETS_CONFIG']['SECRETS_FILE_LOCATION']
        else :
            raise FileNotFoundError("Config file resources/config.ini not found")
