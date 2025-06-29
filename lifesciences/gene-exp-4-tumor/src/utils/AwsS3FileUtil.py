import boto3
import os
import argparse
from io import BytesIO
from dotenv import load_dotenv
from pathlib import Path
from mypy_boto3_s3 import S3Client

from botocore.exceptions import ClientError

from utils.SecretsLoader import SecretsLoader
from utils.AppConfigParser import AppConfigParser

load_dotenv()

# SECRETS_FILE_LOCATION = '/run/secrets/app_secrets'

# AWS_ACCESS_KEY= secrets_loader.AWS_ACCESS_KEY #os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY= secrets_loader.AWS_SECRET_ACCESS_KEY # os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_DEFAULT_REGION= os.getenv('AWS_DEFAULT_REGION')
AWS_DEFAULT_ENCRYPT_ALGO = 'AES256'

class AwsS3FileUtil :

    def __init__(self, config_parser:AppConfigParser, secrets_loader: SecretsLoader) :
        self.config_parser = config_parser
        self.secrets_loader = SecretsLoader(config_parser.secrets_file_loc)
        self.region = config_parser.aws_default_region



    def create_s3_client(self) -> S3Client :
        # s3_client = boto3.client('s3', region_name=region)
        s3_client = boto3.client('s3',
                                region_name=self.region,
                                aws_access_key_id=self.secrets_loader.AWS_ACCESS_KEY,
                                aws_secret_access_key=self.secrets_loader.AWS_SECRET_ACCESS_KEY)
        return s3_client


    def upload_file_with_structure(self,
                                   local_file_path,
                                   bucket_name:str,
                                   s3_key:str,
                                   create_folders=True):
        """
        Upload a file to S3, creating bucket and directory structure if needed.

        Args:
            local_file_path (str): Path to local file to upload
            bucket_name (str): Name of the S3 bucket
            s3_key (str): S3 object key (path) for the file
            region (str): AWS region
            create_folders (bool): Whether to create folder markers

        Returns:
            bool: True if successful, False otherwise
        """

        s3_client = self.create_s3_client()

        # 1: Verify local file exists
        if not os.path.exists(local_file_path):
            print(f"Error: Local file '{local_file_path}' does not exist")
            return False

        # 2: create bucket if it does not exist
        self.create_bucket_if_not_exists(s3_client=s3_client, bucket_name=bucket_name)

        # 3: Create directory structure if requested
        if create_folders:
            self.create_directory_structure(s3_client=s3_client, bucket_name=bucket_name, s3_key=s3_key)

        # 4: Upload the file
        return self.upload_file(s3_client, bucket_name, local_file_path, s3_key)



    def create_bucket_if_not_exists(self, s3_client: S3Client, bucket_name:str) :
        # Step 2: Create bucket if it doesn't exist
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' exists")
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])

            if error_code == 404:
                try:
                    if self.region == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    print(f"Created bucket '{bucket_name}'")
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    return False
            else:
                print(f"Error accessing bucket: {e}")
                return False


    def create_directory_structure(self, s3_client:S3Client, bucket_name, s3_key:str):
        """
        Create directory structure in S3 by creating folder marker objects.

        Args:
            s3_client: Boto3 S3 client
            bucket_name (str): Name of the S3 bucket
            s3_key (str): Directory path to create
        """
        # Extract directory path from s3_key
        s3_dir_path = '/'.join(s3_key.split('/')[:-1])
        if not s3_dir_path:
            return

        # Split path into components
        path_parts = s3_dir_path.strip('/').split('/')
        current_path = ""

        for folder in path_parts:
            current_path += folder + "/"

            try:
                # Check if folder marker exists
                s3_client.head_object(Bucket=bucket_name, Key=current_path)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Create folder marker
                    try:
                        s3_client.put_object(
                            Bucket=bucket_name,
                            Key=current_path,
                            Body=b'',
                            ContentType='application/x-directory'
                        )
                        print(f"Created directory: {current_path}")
                    except ClientError as put_error:
                        print(f"Warning: Could not create directory marker {current_path}: {put_error}")



    def upload_file(self,
                    s3_client:S3Client,
                    bucket_name:str,
                    local_file_path:str,
                    s3_key:str,
                    encrypt_algo:str=AWS_DEFAULT_ENCRYPT_ALGO) :

        try:
            # Get file size for progress tracking
            file_size = os.path.getsize(local_file_path)

            s3_client.upload_file(
                local_file_path,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': AWS_DEFAULT_ENCRYPT_ALGO  # Optional: encrypt at rest
                }
            )

            print(f"Successfully uploaded '{local_file_path}' to 's3://{bucket_name}/{s3_key}'")
            print(f"File size: {file_size:,} bytes")
            return True

        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False




    def upload_multiple_files(self, file_mappings, bucket_name):
        """
        Upload multiple files with their directory structures.

        Args:
            file_mappings (dict): Dictionary mapping local_path -> s3_key
            bucket_name (str): Name of the S3 bucket
            region (str): AWS region

        Returns:
            dict: Results of upload operations
        """
        results = {}

        for local_path, s3_key in file_mappings.items():
            print(f"\nUploading {local_path} -> s3://{bucket_name}/{s3_key}")
            success = self.upload_file_with_structure(local_path, bucket_name, s3_key)
            results[local_path] = success

        return results



    def read_file(self, bucket_name:str, s3_key:str) -> BytesIO :
        try :
            s3_client = self.create_s3_client()
            obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            return BytesIO(obj['Body'].read())
        except Exception as e :
            print(f"Failed to read the file {bucket_name}/{s3_key} from AWS S3")
            raise e



    def generate_cli_commands(self, local_file_path, bucket_name, s3_key):
        """
        Generate equivalent AWS CLI commands.

        Returns:
            str: AWS CLI commands
        """
        commands = []

        # Create bucket
        if self.region == 'us-east-1':
            commands.append(f"aws s3 mb s3://{bucket_name} 2>/dev/null || true")
        else:
            commands.append(f"aws s3 mb s3://{bucket_name} --region {self.region} 2>/dev/null || true")

        # Extract directory path and create folders
        s3_dir_path = '/'.join(s3_key.split('/')[:-1])
        if s3_dir_path:
            path_parts = s3_dir_path.strip('/').split('/')
            current_path = ""
            for folder in path_parts:
                current_path += folder + "/"
                commands.append(f"aws s3api put-object --bucket {bucket_name} --key {current_path} --content-type 'application/x-directory' 2>/dev/null || true")

        # Upload file
        commands.append(f"aws s3 cp '{local_file_path}' s3://{bucket_name}/{s3_key} --sse AES256")

        return '\n'.join(commands)


# Usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script to upload files to AWS S3")
    parser.add_argument("--key", type=str,
                      help="Provide the file to upload along with the path from the bucket in S3. Eg: gene-exp-4-tumor/models1/xgb_GridSearch_Pipeline.pkl",
                      required=True)
    parser.add_argument("--bucket", type=str,
                      help="Provide the S3 bucket to which the file should be uploaded to. This is the root folder where above param 'key' is created. Eg: mlai-projects",
                      required=True)
    parser.add_argument("--upload_file", type=str,
                      help="Provide the relative local file path to upload to S3. Eg: models/xgb_GridSearch_Pipeline.pkl",
                      required=True)
    args = parser.parse_args()

    local_file = args.upload_file
    bucket_name = args.bucket
    s3_key = args.key
    region = "us-east-1"

    ## Expected structure : mlai-projects/gene-exp-4-tumor/models
    # local_file = "models/xgb_GridSearch_Pipeline.pkl"
    # bucket_name = "mlai-projects"
    # s3_key = "gene-exp-4-tumor/models1/xgb_GridSearch_Pipeline.pkl"

    # Add support for multiple files, in case we go with multiple versions
    print(f"\nfiles upload")
    print("=" * 40)

    file_mappings = {
        # "models/xgb_GridSearch_Pipeline.pkl": "gene-exp-4-tumor/models1/xgb_GridSearch_Pipeline.pkl",
        local_file : s3_key
    }

    config_parser: AppConfigParser = AppConfigParser()
    secrets_loader: SecretsLoader = SecretsLoader(config_parser.secrets_file_loc)
    aws_util:AwsS3FileUtil = AwsS3FileUtil(config_parser, secrets_loader)
    results = aws_util.upload_multiple_files(file_mappings, bucket_name)

    print(f"\nUpload Results:")
    for file_path, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {file_path}")


    # read the file back
    bio:BytesIO = aws_util.read_file(bucket_name, s3_key=s3_key)
    if bio is None:
        raise LookupError('Unable to lookup the bucket and file in S3')
    else :
        print("✅ Successfully read the file from S3.")


    # Show equivalent CLI commands
    # print(f"\nEquivalent AWS CLI commands:")
    # print("=" * 40)
    # cli_commands = generate_cli_commands(local_file, bucket_name, s3_key, region)
    # print(cli_commands)

    # # Cleanup demo files
    # import shutil
    # shutil.rmtree("data", ignore_errors=True)
    # shutil.rmtree("models", ignore_errors=True)