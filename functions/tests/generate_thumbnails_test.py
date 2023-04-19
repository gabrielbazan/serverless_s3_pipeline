import json
import os
from typing import Dict, List
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

from functions.environment import EnvironmentVariable
from functions.generate_thumbnails import handler
from functions.settings import (
    THUMBNAIL_SIZES,
    THUMBNAILS_BUCKET_FILE_FOLDER_NAME_TEMPLATE,
    THUMBNAILS_BUCKET_FOLDER_PATH,
)

MODULE = "functions.generate_thumbnails"


MESSAGE_ID = "dummy_message_id"
BUCKET_NAME = "dummy_bucket_name"

EXTENSION = ".extension"
FILENAME = f"remote_filename{EXTENSION}"
OBJECT_KEY = f"/path/to/remote/file/{FILENAME}"

EVENT_MOCK = {
    "Records": [
        {
            "messageId": MESSAGE_ID,
            "body": json.dumps(
                {
                    "Records": [
                        {
                            "s3": {
                                "bucket": {
                                    "name": BUCKET_NAME,
                                },
                                "object": {
                                    "key": OBJECT_KEY,
                                },
                            }
                        }
                    ]
                }
            ),
        }
    ]
}


class GenerateThumbnailsTestCase(TestCase):
    @patch(f"{MODULE}.logging", MagicMock())
    @patch(f"{MODULE}.upload_file_to_s3_bucket")
    @patch(f"{MODULE}.get_environment_variable_or_raise")
    @patch(f"{MODULE}.Image")
    @patch(f"{MODULE}.download_file_from_s3_bucket")
    @patch(f"{MODULE}.TemporaryDirectory")
    def test_handler(
        self,
        TemporaryDirectory: MagicMock,
        download_file_from_s3_bucket: MagicMock,
        Image: MagicMock,
        get_environment_variable_or_raise: MagicMock,
        upload_file_to_s3_bucket: MagicMock,
    ) -> None:
        # Given
        temporary_directory = MagicMock()
        tmp_folder_path = "/tmp/folder/path"
        temporary_directory.__enter__.return_value = tmp_folder_path
        TemporaryDirectory.return_value = temporary_directory

        local_file_path = os.path.join(tmp_folder_path, FILENAME)

        image = MagicMock()
        Image.open.return_value = image
        image.copy.return_value = image

        thumbnails_bucket_name = Mock()
        get_environment_variable_or_raise.return_value = thumbnails_bucket_name

        context = Mock()

        # When
        response = handler(EVENT_MOCK, context)

        # Then
        TemporaryDirectory.assert_called_once_with()

        download_file_from_s3_bucket.assert_called_once_with(
            BUCKET_NAME,
            OBJECT_KEY,
            local_file_path,
        )

        Image.open.assert_called_once_with(local_file_path)

        self.assertEqual(image.copy.call_count, 3)
        image.thumbnail.assert_has_calls([call(size) for size in THUMBNAIL_SIZES])
        image.save.assert_has_calls(
            [
                call(os.path.join(tmp_folder_path, f"{width}x{height}{EXTENSION}"))
                for width, height in THUMBNAIL_SIZES
            ]
        )

        get_environment_variable_or_raise.assert_has_calls(
            [call(EnvironmentVariable.THUMBNAILS_BUCKET_NAME)] * len(THUMBNAIL_SIZES)
        )

        upload_file_to_s3_bucket.assert_has_calls(
            [
                call(
                    # TODO: Duplicated
                    os.path.join(tmp_folder_path, f"{width}x{height}{EXTENSION}"),
                    thumbnails_bucket_name,
                    os.path.join(
                        THUMBNAILS_BUCKET_FOLDER_PATH,
                        THUMBNAILS_BUCKET_FILE_FOLDER_NAME_TEMPLATE.format(FILENAME),
                        # TODO: Duplicated
                        f"{width}x{height}{EXTENSION}",
                    ),
                )
                for width, height in THUMBNAIL_SIZES
            ]
        )

        expected_response: Dict[str, List[str]] = {"batchItemFailures": []}
        self.assertEqual(response, expected_response)