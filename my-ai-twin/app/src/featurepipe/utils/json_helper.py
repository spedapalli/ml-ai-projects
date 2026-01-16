import json

from featurepipe.datasetgen.exceptions import JSONDecodeError

class JSONFileHandler :

    def read_json(self, filename: str) -> list :
        try :
            with open(filename, 'r') as file :
                json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{filename}' does not exist")
        except json.JSONDecodeError as je:
            raise je


    def write_json(self, filename: str, data: list):
        with open(filename, 'w') as file :
            json.dump(data, file, indent=4)
