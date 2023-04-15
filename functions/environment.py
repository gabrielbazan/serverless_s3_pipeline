from os import environ


class EnvironmentVariable:
    AWS_ENDPOINT_URL: str = "AWS_ENDPOINT_URL"
    THUMBNAILS_BUCKET_NAME: str = "THUMBNAILS_BUCKET_NAME"
    IMAGES_QUEUE_URL: str = "IMAGES_QUEUE_URL"
    IMAGES_DLQ_URL: str = "IMAGES_DLQ_URL"


def get_environment_variable_or_raise(name: str) -> str:
    assert name in environ, f"{name} environment variable is not set"
    return environ[name]
