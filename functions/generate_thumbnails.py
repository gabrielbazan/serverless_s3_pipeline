import json
from collections import namedtuple
from os.path import basename, dirname, join, splitext
from tempfile import TemporaryDirectory
from typing import Any, Dict, Generator, List, Tuple

from PIL import Image

from functions.aws import download_file_from_s3_bucket, upload_file_to_s3_bucket
from functions.environment import EnvironmentVariable, get_environment_variable_or_raise
from functions.settings import (
    THUMBNAIL_SIZES,
    THUMBNAILS_BUCKET_FILE_FOLDER_NAME_TEMPLATE,
    THUMBNAILS_BUCKET_FOLDER_PATH,
)

RemoteFile = namedtuple("RemoteFile", ["bucket_name", "file_path"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    for remote_file in get_files_from_event(event):
        process_file(remote_file)

    return {"body": "Success", "statusCode": 200}


def get_files_from_event(event: Dict[str, Any]) -> Generator[RemoteFile, None, None]:
    for record in event["Records"]:
        body = record["body"]
        body_json = json.loads(body)

        body_records = body_json["Records"]

        for body_record in body_records:
            s3 = body_record["s3"]

            bucket_name = s3["bucket"]["name"]
            file_path = s3["object"]["key"]

            yield RemoteFile(bucket_name, file_path)


def process_file(remote_file: RemoteFile) -> None:
    with TemporaryDirectory() as folder_path:
        local_file_path = download_file(remote_file, folder_path)
        thumbnails_paths = generate_thumbnails(local_file_path)
        upload_thumbnails(remote_file, thumbnails_paths)


def download_file(remote_file: RemoteFile, folder_path: str) -> str:
    filename = basename(remote_file.file_path)
    local_file_path = join(folder_path, filename)

    download_file_from_s3_bucket(
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

    template = THUMBNAILS_BUCKET_FILE_FOLDER_NAME_TEMPLATE
    remote_thumbnails_folder_name = template.format(file_name)

    thumbnail_filename = basename(local_thumbnail_path)

    remote_thumbnail_path = join(
        THUMBNAILS_BUCKET_FOLDER_PATH,
        remote_thumbnails_folder_name,
        thumbnail_filename,
    )

    thumbnails_bucket_name = get_environment_variable_or_raise(
        EnvironmentVariable.THUMBNAILS_BUCKET_NAME
    )

    upload_file_to_s3_bucket(
        local_thumbnail_path,
        thumbnails_bucket_name,
        remote_thumbnail_path,
    )
