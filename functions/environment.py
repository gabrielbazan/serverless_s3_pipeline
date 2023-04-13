from os import environ


class EnvironmentVariable:
    AWS_ENDPOINT_URL = "AWS_ENDPOINT_URL"
    THUMBNAILS_BUCKET_NAME = "THUMBNAILS_BUCKET_NAME"


def get_environment_variable_or_raise(name: str) -> str:
    assert name in environ, f"{name} environment variable is not set"
    return environ[name]
