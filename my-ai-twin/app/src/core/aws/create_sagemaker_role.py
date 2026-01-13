import boto3
import json
from pathlib import Path

from core.logger_utils import get_logger
from core.config import settings

logger = get_logger(__file__)

try :
    import boto3
except ModuleNotFoundError:
    logger.warning(
        "Unable to load AWS or SageMaker library, boto3. Run 'poetry install --with aws' to support AWS")



def create_sagemaker_role(username: str):
    assert settings.AWS_ACCESS_KEY, "AWS_ACCESS_KEY is not configured."
    assert settings.AWS_SECRET_KEY, "AWS_SECRET_KEY is not configured."
    assert settings.AWS_REGION, "AWS_REGION is not configured."

    # create boto3 client
    iam = boto3.client("iam",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY,
                    aws_secret_access_key=settings.AWS_SECRET_KEY)


    # create IAM user
    iam.create_user(UserName=username)

    # policies
    policies = [
        "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
        "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess",
        "arn:aws:iam::aws:policy/IAMFullAccess",
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    ]

    for policy in policies:
        iam.attach_user_policy(UserName=username, PolicyArn=policy)


    access_key_response = iam.create_access_key(UserName=username)
    access_key = access_key_response["AccessKey"]

    logger.info(f"User {username} successfully created")
    logger.info("Access Key ID and Secret Access Key successfully created")

    return {
        "AccessKeyId": access_key['AccessKeyId'],
        "SecretAccessKey": access_key['SecretAccessKey']
    }


if __name__ == "__main__":
    user_name = "sagemaker-deployer"
    file_name = "sagemaker-deployer_credentials.json"
    new_user = create_sagemaker_role(user_name)

    with Path(file_name).open("w") as f :
        json.dump(new_user, f)

    logger.info(f"Credentials saved to file at {file_name}")