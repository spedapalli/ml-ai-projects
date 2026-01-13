
from tqdm import tqdm
import tempfile
import os
import random
import json

from core.logger_utils import get_logger
from core.config import settings

logger = get_logger(__name__)

try :
    import opik
    from comet_ml import Experiment
    from opik.configurator.configure import OpikConfigurator
    from opik.rest_helpers import OpikRestHelpers

except Exception as e:
    logger.error(f"Failed to import opik: {e}")
    raise

def configre_opik() -> None:
    if settings.COMET_API_KEY and settings.COMET_PROJECT_NAME:
        if settings.COMET_WORKSPACE:
            default_workspace = settings.COMET_WORKSPACE
        else:
            try :
                client = OpikConfigurator(api_key=settings.COMET_API_KEY, project_name=settings.COMET_PROJECT_NAME)
                default_workspace = client._get_default_workspace()
            except Exception as e :
                logger.warning("Default workspace not found. Setting workspace to None and enabling interactive mode.")
                default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT_NAME

        opik.configure(api_key=settings.COMET_API_KEY,
            workspace=default_workspace,
            use_local=False,
            force=True)

        logger.info("Successfully configured opik")

    else :
        logger.warning(
            "COMET_API_KEY and / or COMET_PROJECT_NAME are not set. Set them to enable prompt monitoring using Opik (the open source version of Comet ML)"
        )


def create_dataset_from_artifacts(dataset_name:str, artifact_names: list[str]) -> opik.Dataset | None:
    """
    Creates a dataset from artifacts in Opik, specifically testing artifact only.
    """
    client = opik.Opik()
    try :
        dataset = client.get_dataset(name=dataset_name)
    except Exception :
        dataset = None

    if dataset:
        logger.warning(f"Dataset {dataset_name} already exists. Skipping dataset creation....")
        return dataset


    experiment = Experiment(api_key=settings.COMET_API_KEY,
                            project_name=settings.COMET_PROJECT_NAME,
                            workspace=settings.COMET_WORKSPACE) # shud this be default workspace, case where this var is not configured ?

    dataset_items = []
    with tempfile.TemporaryDirectory() as tmp_dir :
        # download artifacts in Opik
        for artifact_name in tqdm(artifact_names) :
            artifact_dir = Path(tmp_dir) / artifact_name
            try :
                logged_artifact = experiment.get_artifact(artifact_name)
                logged_artifact.download(artifact_dir)
                logger.info(f"Successfully downloaded artifact {artifact_name} at location {tmp_dir}")
            except Exception as e :
                logger.error(f"Error downloading artifact {artifact_name}: {str(e)}")
                continue

            # get only Testing json file
            testing_artifact_file = list(artifact_dir.glob("*_testing.json"))
            assert (len(testing_artifact_file) == 1), "Expected exactly one testing artifact file"
            testing_artifact_file = testing_artifact_file[0]

            logger.info(f"Loading testing data from artifact file : {testing_artifact_file}")
            with open(testing_artifact_file, "r") as file:
                items = json.load(file)

            enhanced_items = [
                {**item, "artifact_name": artifact_name} for item in items
            ]
            dataset_items.extend(enhanced_items)

    experiment.end()

    if (len(dataset_items) == 0) :
        logger.warning("No items found in the dataset. Skipping dataset creation....")
        return None

    dataset = client.create_dataset(name=dataset_name,
                                    description = "Dataset created from artifacts",
                                    items=dataset_items)
    return dataset

def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset | None:
    client = opik.Opik()
    dataset = client.get_or_create_dataset(name = name, description = description)
    dataset.insert(items)

    dataset = client.get_dataset(name = name)
    return dataset


def add_to_dataset_with_sampling(item:dict, dataset_name: str) -> bool:
    # 70% of the time, add to dataset
    if "1" in random.choices(["0", "1"], weights=[0.3, 0.7]):
        client = opik.Opik()
        dataset = client.get_or_create_dataset(name = dataset_name)
        dataset.insert([item])

        return True
    return False