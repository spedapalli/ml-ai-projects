import logging
import os
from dotenv import load_dotenv
import argparse
import boto3
from boto3.s3.transfer import TransferConfig
from mypy_boto3_s3 import S3Client
from botocore.exceptions import ClientError


load_dotenv()

# for now set a default val
BYTE_MULTIPLE = 25
# credentials are defined in ~/.aws/credentials file
AWS_ACCESS_KEY= os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN= os.getenv('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION= os.getenv('AWS_DEFAULT_REGION')



def upload_file(file_name: str, bucket_name: str, object_name: str, folder_path:str='mlai-projects/gene-exp-4-tumor', region_name:str=AWS_DEFAULT_REGION) :
    '''
    @param file_name : Name of the file
    @param bucket_name : S3 bucket to which the file needs to be dropped into
    @param object_name : Unique Id given to the file
    @param region_name :
    '''

    s3_client = boto3.client('s3',
                             region_name=region_name,
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY) #,
                             # aws_session_token=AWS_SESSION_TOKEN)

    create_bucket_if_not_exists(s3_client, bucket_name=bucket_name, folder_path=folder_path, region_name=region_name)

    if (object_name is None):
        object_name = os.path.basename(file_name)


    config = TransferConfig(
        multipart_threshold=1024 * BYTE_MULTIPLE,  # 25MB
        max_concurrency=10,
        multipart_chunksize=1024 * BYTE_MULTIPLE,
        use_threads=True
    )

    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name, config)
    except ClientError as ce:
        logging.error(ce)
        raise ce


# def bucket_exists(s3_client, bucket_name: str) :
#     try :
#         s3_client.head_bucket(Bucket=bucket_name)
#         return True
#     except ClientError as ce :
#         error_code = ce.response['Error']['Code']
#         if error_code == 404:
#             return False
#         elif error_code == 403:
#             print(f"Access denied to given bucket {bucket_name}")
#             return True
#         else :
#             print(f"Error checking if {bucket_name} exists or not.")
#             return False


def bucket_and_folder_exist(s3_client:S3Client, bucket_name:str, folder_path:str):
    try :
        s3_client.head_bucket(Bucket=bucket_name, Key=folder_path)
        return True
    except ClientError as ce :
        error_code = ce.response['Error']['Code']
        if error_code == 404:
            return False
        elif error_code == 403:
            print(f"Access denied to given bucket {bucket_name}")
            return True
        else :
            print(f"Error checking if {bucket_name} exists or not.")
            return False


def create_folder_bucket(s3_client:S3Client, bucket_name:str, folder_path:str, region=AWS_DEFAULT_REGION) :
    create_bucket(s3_client, bucket_name, folder_path, region)
    try :
        s3_client.put_object(Bucket=bucket_name,
                                Key=folder_path,
                                Body=b'',
                                ContentType='application/x-directory')
        print(f"Created folder: {folder_path}")
    except ClientError as put_err:
        print(f"Error creating folder {folder_path}: {put_err}")
        return False



def create_bucket(s3_client:S3Client, bucket_name:str, region=AWS_DEFAULT_REGION) :
    if region == AWS_DEFAULT_REGION:
        s3_client.create_bucket(Bucket=bucket_name)
    else :
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=({'LocationConstraint':region}))


def create_folder_structure_if_not_exists(s3_client:S3Client, bucket_name:str, folder_path:str):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=folder_path)
        print(f"Folder '{folder_path}' already exists")
    except ClientError as ce:
        if ce.response['Error']['Code'] == '404':
            try :
                s3_client.put_object(Bucket=bucket_name,
                                        Key=folder_path,
                                        Body=b'',
                                        ContentType='application/x-directory')
                print(f"Created folder: {folder_path}")
            except ClientError as put_err:
                print(f"Error creating folder {folder_path}: {put_err}")
                return False
        else :
            print(f"Error checking folder {folder_path}: {ce}")
            return False


# Claude code - to understand how this directory structure works
def create_folder_structure(s3_client:S3Client, bucket_name:str, folder_path:str):
    folder_parts = folder_path.strip('/').split('/')
    current_path = ''

    for folder in folder_parts:
        current_path += folder + '/'
        try:
            s3_client.head_object(Bucket=bucket_name, Key=current_path)
            print(f"Folder '{current_path}' already exists")
        except ClientError as ce:
            if ce.response['Error']['Code'] == '404':
                try :
                    s3_client.put_object(Bucket=bucket_name,
                                         Key=current_path,
                                         Body=b'',
                                         ContentType='application/x-directory')
                    print(f"Created folder: {current_path}")
                except ClientError as put_err:
                    print(f"Error creating folder {current_path}: {put_err}")
                    return False
            else :
                print(f"Error checking folder {current_path}: {ce}")
                return False

    return True



# create bucket if it does not exist
def create_bucket_if_not_exists(s3_client:S3Client, bucket_name: str, folder_path:str, region_name='us-east-1'):
    #TODO : Remove below dup of creating client
    # s3_client = boto3.client('s3',
    #                          region_name=region_name,
    #                          aws_access_key_id=AWS_ACCESS_KEY,
    #                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # TODO : Temp to understand how the logic in below fn works, compared to lines further below
    create_folder_structure(s3_client, bucket_name=bucket_name, folder_path=folder_path)
    # if (bucket_and_folder_exist(s3_client, bucket_name=bucket_name, folder_path=folder_path)):
    #     return True
    # else :
    #     return create_bucket(s3_client, bucket_name, region_name)


    # listing all b
    # try:
    #     # bucket = s3_client.get_object(Bucket=bucket_name)
    #     response = s3_client.head_bucket(Bucket=bucket_name)
    #     if response is not None:
    #         print(f"Bucket {bucket_name} already exists in regions {region_name}")
    #         return True
    #     else :
    #         location = {'LocationConstraint': region_name}
    #         bucket = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

    #         return True
    # except ClientError as ce:
    #     logging.error(ce)
    #     if ce.error
    #     raise ce



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to upload files to AWS S3")
    parser.add_argument("--folder_path", type=str, help="Provide the path to the bucket param in S3", required=True)
    parser.add_argument("--bucket_name", type=str, help="Provide the S3 bucket to which the file should be uploaded to", required=True)
    parser.add_argument("--file_name", type=str, help="Provide the file to upload to S3", required=True)
    # parser.add_argument("--AWS_ACCESS_KEY", type=str, help="Provide the AWS Access Key", required=True)
    # parser.add_argument("--AWS_SECRET_ACCESS_KEY", type=str, help="Provide the AWS Secret Access Key", required=True)
    # parser.add_argument("--AWS_SESSION_TOKEN", type=str, help="Provide the AWS session Token", required=True)

    args = parser.parse_args()

    upload_file(file_name=args.file_name, bucket_name=args.bucket_name, folder_path=args.folder_path, object_name=None)

