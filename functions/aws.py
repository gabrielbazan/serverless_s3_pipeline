from typing import Any, Dict

import boto3

from functions.environment import EnvironmentVariable, get_environment_variable_or_raise


class Service:
    S3: str = "s3"
    SQS: str = "sqs"


def download_file_from_s3_bucket(
    bucket_name: str, remote_path: str, local_path: str
) -> None:
    client = get_client(Service.S3)
    client.download_file(bucket_name, remote_path, local_path)


def upload_file_to_s3_bucket(
    local_path: str, bucket_name: str, remote_path: str
) -> None:
    client = get_client(Service.S3)
    client.upload_file(local_path, bucket_name, remote_path)


def receive_messages_from_sqs_queue(
    queue_url: str,
    max_number_of_messages: int,
    visibility_timeout: int,
    wait_time_seconds: int,
) -> Dict[str, Any]:
    client = get_client(Service.SQS)
    return dict(
        client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time_seconds,
        )
    )


def send_message_to_sqs_queue(queue_url: str, message_body: str) -> None:
    client = get_client(Service.SQS)
    client.send_message(QueueUrl=queue_url, MessageBody=message_body)


def delete_message_from_sqs_queue(queue_url: str, receipt_handle: str) -> None:
    client = get_client(Service.SQS)
    client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def get_client(name: str) -> Any:
    endpoint_url = get_environment_variable_or_raise(
        EnvironmentVariable.AWS_ENDPOINT_URL
    )
    return boto3.client(name, endpoint_url=endpoint_url)
