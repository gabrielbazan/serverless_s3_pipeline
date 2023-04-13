from typing import Any

import boto3

from functions.environment import EnvironmentVariable, get_environment_variable_or_raise


def download_file_from_s3_bucket(
    bucket_name: str, remote_path: str, local_path: str
) -> None:
    client = get_s3_client()
    client.download_file(bucket_name, remote_path, local_path)


def upload_file_to_s3_bucket(
    local_path: str, bucket_name: str, remote_path: str
) -> None:
    client = get_s3_client()
    client.upload_file(local_path, bucket_name, remote_path)


def get_s3_client() -> Any:
    endpoint_url = get_environment_variable_or_raise(
        EnvironmentVariable.AWS_ENDPOINT_URL
    )
    return boto3.client("s3", endpoint_url=endpoint_url)
