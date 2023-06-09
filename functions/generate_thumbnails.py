import json
import logging
from collections import namedtuple
from os.path import basename, dirname, join, splitext
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

from PIL import Image

from functions.aws import download_file_from_s3_bucket, upload_file_to_s3_bucket
from functions.environment import EnvironmentVariable, get_environment_variable_or_raise
from functions.settings import (
    THUMBNAIL_SIZES,
    THUMBNAILS_BUCKET_FILE_FOLDER_NAME_TEMPLATE,
    THUMBNAILS_BUCKET_FOLDER_PATH,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

RemoteFile = namedtuple("RemoteFile", ["bucket_name", "file_path", "message_id"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    remote_files: List[RemoteFile] = get_files_from_event(event)
    failed_files: List[RemoteFile] = process_files(remote_files)
    return build_response(failed_files)


def get_files_from_event(event: Dict[str, Any]) -> List[RemoteFile]:
    return [
        RemoteFile(
            body_record["s3"]["bucket"]["name"],
            body_record["s3"]["object"]["key"],
            record["messageId"],
        )
        for record in event["Records"]
        for body_record in json.loads(record["body"])["Records"]
    ]


def process_files(remote_files: List[RemoteFile]) -> List[RemoteFile]:
    failed_files: List[RemoteFile] = []

    for remote_file in remote_files:
        try_to_process_file(remote_file, failed_files)

    return failed_files


def build_response(failed_files: List[RemoteFile]) -> Dict[str, List[Dict[str, str]]]:
    return {
        "batchItemFailures": [
            {
                "itemIdentifier": failed_file.message_id,
            }
            for failed_file in failed_files
        ]
    }


def try_to_process_file(
    remote_file: RemoteFile, failed_files: List[RemoteFile]
) -> None:
    try:
        process_file(remote_file)
        logging.info("Successfully processed %s", remote_file)
    except Exception:
        logging.error("Failed to process %s", remote_file)
        failed_files.append(remote_file)


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
