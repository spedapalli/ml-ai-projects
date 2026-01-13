import json
from pathlib import Path

from core.logger_utils import get_logger
from core.config import settings

try :
    import boto3
except Exception as e :
    logger.error(
        "Unable to import boto3, needed for AWS or Sagemaker imports. Run 'poetry install --with aws' to support AWS")
    raise


def create_sagemaker_execution_role(role_name: str) :
    assert settings.AWS_REGION, "AWS_REGION is not set"
    assert settings.AWS_ACCESS_KEY, "AWS_ACCESS_KEY is not set"
    assert settings.AWS_SECRET_KEY, "AWS_SECRET_KEY is not set"

    # create IAM client
    iam = boto3.client(
        'iam',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )

    # create trust relationship policy
    trust_relationship = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "sagemaker.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try :
        # Create the IAM role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship),
            description = "Execution role for SageMaker"
        )

        # attach policies
        policies = [
            "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
        ]

        for policy in policies :
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy
            )

        logger.info(f"Role {role_name} created successfully.")
        logger.info(f"Role ARN: {role['Role']['Arn']}")

        return role['Role']['Arn']

    except iam.exceptions.EntityAlreadyExistsException as e :
        logger.warning(f"Role {role_name} already exists. Fetching its ARN....")
        role = iam.get_role(RoleName=role_name)
        return role['Role']['Arn']


if __name__ == "__main__":
    arn_file_name = "sagemaker_execution_role.json"
    role_arn = create_sagemaker_execution_role("sagemaker-execution-role")
    logger.info(f"Role ARN: {role_arn}")

    #save ARN to file
    with Path(arn_file_name).open("w") as f:
        json.dump({"RoleArn": role_arn}, f)

    logger.info(f"Role ARN saved to file: {arn_file_name}")

