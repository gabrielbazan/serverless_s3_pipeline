from typing import Any, Dict, Tuple, List
from collections import namedtuple
import boto3
from os.path import basename, join, dirname, splitext
from os import environ
from tempfile import TemporaryDirectory
from PIL import Image


THUMBNAIL_SIZES = (
    (75, 75),
    (125, 125),
    (1280, 720),
)


AWS_ENDPOINT_URL = environ["AWS_ENDPOINT_URL"]
THUMBNAILS_BUCKET_NAME = environ["THUMBNAILS_BUCKET_NAME"]

THUMBNAILS_BUCKET_FOLDER_PATH = "thumbnails"


RemoteFile = namedtuple("RemoteFile", ["bucket_name", "file_path"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    for remote_file in get_files_from_event(event):
        process_file(remote_file)

    return {"body": "Success", "statusCode": 200}


def get_files_from_event(event):
    for record in event["Records"]:
        s3 = record["s3"]

        bucket = s3["bucket"]
        bucket_name = bucket["name"]

        obj = s3["object"]
        file_path = obj["key"]

        yield RemoteFile(bucket_name, file_path)


def process_file(remote_file: RemoteFile) -> None:
    with TemporaryDirectory() as folder_path:
        local_file_path = download_file(remote_file, folder_path)
        thumbnails_paths = generate_thumbnails(local_file_path)
        upload_thumbnails(remote_file, thumbnails_paths)


def download_file(remote_file: RemoteFile, folder_path: str) -> str:
    filename = basename(remote_file.file_path)
    local_file_path = join(folder_path, filename)

    client = boto3.client("s3", endpoint_url=AWS_ENDPOINT_URL)

    client.download_file(
        remote_file.bucket_name,
        remote_file.file_path,
        local_file_path,
    )

    return local_file_path


def generate_thumbnails(local_file_path: str) -> List[str]:
    image = Image.open(local_file_path)

    return [
        generate_thumbnail(
            image,
            size,
            local_file_path,
        )
        for size in THUMBNAIL_SIZES
    ]


def generate_thumbnail(
    image: Image,
    size: Tuple[int, int],
    local_file_path: str,
) -> str:
    file_name = basename(local_file_path)
    local_folder_path = dirname(local_file_path)

    thumbnail_image = image.copy()

    thumbnail_image.thumbnail(size)

    _, extension = splitext(file_name)
    width, height = size
    thumbnail_filename = f"{width}x{height}{extension}"

    thumbnail_path = join(local_folder_path, thumbnail_filename)

    thumbnail_image.save(thumbnail_path)

    return thumbnail_path


def upload_thumbnails(
    remote_file: RemoteFile,
    thumbnails_paths: List[str],
) -> None:
    for local_thumbnail_path in thumbnails_paths:
        upload_thumbnail(remote_file, local_thumbnail_path)


def upload_thumbnail(
    remote_file: RemoteFile,
    local_thumbnail_path: str,
) -> None:
    file_name = basename(remote_file.file_path)

    remote_thumbnails_folder_name = f"thumbnails_{file_name}"

    thumbnail_filename = basename(local_thumbnail_path)

    remote_thumbnail_path = join(
        THUMBNAILS_BUCKET_FOLDER_PATH,
        remote_thumbnails_folder_name,
        thumbnail_filename,
    )

    client = boto3.client("s3", endpoint_url=AWS_ENDPOINT_URL)
    client.upload_file(
        local_thumbnail_path,
        THUMBNAILS_BUCKET_NAME,
        remote_thumbnail_path,
    )

    print("Uploaded to ", remote_thumbnail_path)
