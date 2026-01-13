import json
from pathlib import Path
from sklearn.model_selection import train_test_split
import comet_ml
# from comet_ml import Artifact, start

from core.logger_utils import get_logger
from core.config import settings
from db.qdrant_connection import QdrantDatabaseConnector

from featurepipe.datasetgen.dataformatter import DataFormatter
from featurepipe.datasetgen.document_chunker import DocumentChunker
from featurepipe.utils.json_helper import JSONFileHandler
from featurepipe.datasetgen.gpt_communicator import GPTCommunicator


logger = get_logger(__name__)

client = QdrantDatabaseConnector()

class DatasetGenerator:
    """The class reads cleaned dataset stored in Vector Db, formats the prompt before sending it to OpenAI GPT,
    splits the content into train and test and writes this data to Comet.
    """
    def __init__(self,
                 json_handler: JSONFileHandler,
                 data_formatter: DataFormatter,
                 gpt_communicator: GPTCommunicator) -> None:

        self.json_handler = json_handler
        self.data_formatter = data_formatter
        self.gpt_communicator = gpt_communicator



    def generate_training_data(self, collection_name: str, data_type: str, batch_size: int = 3) -> None:
        """ Retrieves the cleaned content in Vector DB, generates training and test data and pushes this to Comet.

        Args:
            collection_name (str): Underlying connection name - articles, posts, repositories etc.
            data_type (str): _description_
            batch_size (int, optional): _description_. Defaults to 3.
        """
        assert(settings.COMET_API_KEY), "COMET_API_KEY key is not set. Please set the value in your .env file."
        assert(settings.COMET_WORKSPACE), "COMET_WORKSPACE key is not set. Please set the value in your .env file."
        assert(settings.COMET_PROJECT), "COMET_PROJECT key is not set. Please set the value in your .env file."
        assert(settings.OPENAI_API_KEY), "OPEN_API_KEY key is not set. Please set the value in your .env file."

        cleaned_documents = self.fetch_all_cleaned_content(collection_name)
        cleaned_documents = DocumentChunker().chunk_documents(cleaned_documents)
        num_cleaned_documents = len(cleaned_documents)

        generated_instruct_dataset = []
        for i in range (0, num_cleaned_documents, batch_size):
            batch = cleaned_documents[i : i + batch_size]
            prompt = self.data_formatter.format_prompt(batch, data_type, i)
            batch_instructions = self.gpt_communicator.send_prompt(prompt)

            if (len(batch_instructions) != len(batch)):
                logger.error(
                    f"Received {len(batch_instructions)} instructions for {len(batch)} documents.\
                        Skipping this batch....")
                continue

            for instruction, content in zip(batch_instructions, batch):
                instruction["content"] = content
                generated_instruct_dataset.append(instruction)

        train_test_data = self._split_dataset(generated_instruct_dataset)
        self.push_to_comet(train_test_data, data_type, collection_name)


    def _split_dataset(self, generated_instruct_dataset: list[dict], test_size: float = 0.2) -> tuple[list[dict], list[dict]]:

        if len(generated_instruct_dataset) == 0 :
            return [],[]

        train_data, test_data = train_test_split(generated_instruct_dataset, test_size=test_size, random_state=42)
        return train_data, test_data


    def push_to_comet(self,
                      train_test_data: tuple[list[dict], list[dict]],
                      data_type: str,
                      collection_name: str,
                      output_dir: Path = Path("generated_dataset")) -> None:

        output_dir.mkdir(exist_ok = True)

        try :
            logger.info(f"Starting to push data to comet: {collection_name}")
            comet_ml.login()
            experiment = comet_ml.start()

            train_data, test_data = train_test_data
            train_data_file_name = output_dir / f"{collection_name}_train.json"
            test_data_file_name = output_dir / f"{collection_name}_test.json"

            logger.info(f"Writing training data to file {train_data_file_name}")
            with train_data_file_name.open("w") as file :
                json.dump(train_data, file)

            logger.info(f"Writing testing data to file {test_data_file_name}")
            with test_data_file_name.open('w') as file :
                json.dump(test_data, file)

            logger.info("Train and Test data written successfully to files")

            artifact = comet_ml.Artifact(f"{data_type}-instruct-dataset")
            artifact.add(train_data_file_name)
            artifact.add(test_data_file_name)
            logger.info("Artifact created with Train and Test data.")

            experiment.log_artifact(artifact)
            experiment.end()
            logger.info("Artifact pushed to Comet successfully.")

        except Exception:
            logger.exception(f"Failed to create Comet artifact and push Test and Train data to Comet.")


    def fetch_all_cleaned_content(self, collection_name:str) -> list:
        """Retrieves cleaned content persisted in Qdrant Db

        Args:
            collection_name (str): Collection name in QDrant Db. eg: articles, posts, repositories etc..

        Returns:
            list: list of cleaned content of the given collection_name
        """
        all_cleaned_contents = []

        scroll_response: tuple = client.scroll(collection_name=collection_name, limit=10000)
        points = scroll_response[0]

        for point in points:
            cleaned_content = point.payload["cleaned_content"]
            if cleaned_content:
                all_cleaned_contents.append(cleaned_content)

        return all_cleaned_contents


if __name__ == "__main__":
    json_handler = JSONFileHandler()
    gpt_communicator = GPTCommunicator()
    data_formatter = DataFormatter()
    dataset_generator = DatasetGenerator(json_handler, data_formatter, gpt_communicator)

    collections = [
        ("cleaned_articles", "articles"),
        ("cleaned_repositories", "repositories"),
    ]

    for collection_name, data_type in collections:
        logger.info(
            "Generated training data",
            collection_name = collection_name,
            data_type = data_type,
        )

        dataset_generator.generate_training_data(collection_name=collection_name, data_type=data_type)



