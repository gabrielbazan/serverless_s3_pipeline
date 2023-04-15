import logging
from typing import Any, Dict, List

from functions.aws import (
    delete_message_from_sqs_queue,
    receive_messages_from_sqs_queue,
    send_message_to_sqs_queue,
)
from functions.environment import EnvironmentVariable, get_environment_variable_or_raise

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


MAX_NUMBER_OF_MESSAGES = 5
VISIBILITY_TIMEOUT = 5
WAIT_TIME_SECONDS = 3


# TODO: What if I sent it back to the queue, but fails to delete from the DLQ?


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    queue_url = get_environment_variable_or_raise(EnvironmentVariable.IMAGES_QUEUE_URL)
    dlq_url = get_environment_variable_or_raise(EnvironmentVariable.IMAGES_DLQ_URL)

    retried_messages_count = 0

    messages = get_messages_from_dlq(dlq_url)

    while messages:
        process_messages(messages, queue_url, dlq_url)
        retried_messages_count += len(messages)
        messages = get_messages_from_dlq(dlq_url)

    return {
        "statusCode": 200,
        "body": {
            "retriedMessagesCount": retried_messages_count,
        },
    }


def get_messages_from_dlq(dlq_url: str) -> List[Dict[str, Any]]:
    response = receive_messages_from_sqs_queue(
        dlq_url,
        MAX_NUMBER_OF_MESSAGES,
        VISIBILITY_TIMEOUT,
        WAIT_TIME_SECONDS,
    )
    return response.get("Messages", [])


def process_messages(
    messages: List[Dict[str, Any]],
    queue_url: str,
    dlq_url: str,
) -> None:
    for message in messages:
        process_message(message, queue_url, dlq_url)


def process_message(
    message: Dict[str, Any],
    queue_url: str,
    dlq_url: str,
) -> None:
    message_id = message["MessageId"]

    logging.info("[%s] Sending message to queue", message_id)
    send_message_to_sqs_queue(queue_url, message["Body"])

    logging.info("[%s] Deleting message from DLQ", message_id)
    delete_message_from_sqs_queue(dlq_url, message["ReceiptHandle"])

    logging.info("[%s] Successfully processed message", message_id)
