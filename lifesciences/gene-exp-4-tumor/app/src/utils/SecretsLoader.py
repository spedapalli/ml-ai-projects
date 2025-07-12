import os
import threading
from typing import Dict
from dotenv import load_dotenv


# using metaclass to control the creation of the SecretsLoader class
class SecretsLoaderMetaClass(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]



class SecretsLoader (metaclass=SecretsLoaderMetaClass):

    def __init__(self, file_path:str):
        if hasattr(self, 'initialized'):
            return

        self.load_secrets(file_path)


    def load_secrets(self, file_path='/run/secrets/app_secrets'):

        if (os.path.isfile(file_path)):
            print(f"file {file_path} is found to exist. Loading secrets from the file.")
            self.load_from_secrets_file(file_path)
        else :
            print(f"File {file_path} was not found. Hence loading from environment.")
            load_dotenv()
            self.load_from_env()


    def load_from_secrets_file(self, file_path='/run/secrets/app_secrets') :
        try :
            with open(file_path) as file :
                content = file.read()
                for line in content.splitlines() :
                    print(f"{'=' * 20} Processing line {line} {'=' * 20}")
                    if '=' in line :
                        key, value = line.split('=', 1)
                        if key == 'AWS_ACCESS_KEY_ID':
                            self.AWS_ACCESS_KEY_ID = value
                        elif key == 'AWS_SECRET_ACCESS_KEY':
                            self.AWS_SECRET_ACCESS_KEY = value
        except FileNotFoundError as fe :
            print("File is not found. Please check if file exists: \n", fe)
            raise fe
        except Exception as e:
            print("An unknown exception occured while loading Secrets")
            raise e


    def load_from_env(self):
        # make sure these env vars are not set on terminal, which takes precedence over .env file
        self.AWS_ACCESS_KEY= os.getenv('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')

