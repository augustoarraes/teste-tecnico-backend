import json

import boto3

from core.config import settings


def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=settings.AWS_REGION,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def get_queue_url() -> str:
    client = get_sqs_client()
    response = client.get_queue_url(QueueName=settings.SQS_PROPOSALS_QUEUE_NAME)
    return response["QueueUrl"]


def send_message(message: dict) -> dict:
    client = get_sqs_client()
    queue_url = get_queue_url()

    return client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
    )