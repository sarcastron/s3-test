"""S3 client for testing keys"""

import io
from pathlib import Path
import boto3
from botocore.client import Config, ClientError


class TestS3Client:
    """
    S3 client
    """

    def __init__(
        self,
        bucket: str,
        access_key: str | None = None,
        hmac_secret: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:

        self.bucket = bucket

        self._client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=hmac_secret,
            endpoint_url=endpoint_url,
            region_name="us-central1",
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )
        # Immediate validation check
        self._validate_connection()

    def _validate_connection(self):
        """Checks if the keys and signature work by hitting the bucket metadata."""
        try:
            self._client.head_bucket(Bucket=self.bucket)
            print(f"✅ Successfully authenticated and verified bucket: {self.bucket}")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "403":
                print("❌ Access Denied: Check IAM permissions on the bucket.")
            elif error_code == "SignatureDoesNotMatch":
                print(
                    "❌ Signature Error: Access Key/Secret or Addressing Style is wrong."
                )
            raise e

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        List objects in the bucket, optionally filtered by prefix.

        Returns a list of dicts with keys: Key, Size, LastModified, ETag.
        Handles pagination automatically.
        """
        results = []
        paginator = self._client.get_paginator("list_objects_v2")

        pages = paginator.paginate(
            Bucket=self.bucket,
            Prefix=prefix,
            PaginationConfig={"MaxItems": max_keys},
        )

        for page in pages:
            for obj in page.get("Contents", []):
                results.append(
                    {
                        "Key": obj["Key"],
                        "Size": obj["Size"],
                        "LastModified": obj["LastModified"],
                        "ETag": obj["ETag"].strip('"'),
                    }
                )

        return results

    def download_object(self, key: str, dest: str | Path | None = None) -> Path:
        """
        Download an object from the bucket to a local file.

        Args:
            key:  The S3 object key to download.
            dest: Local destination path (file or directory).
                  Defaults to the current working directory using the
                  object's basename as the filename.

        Returns:
            The resolved Path of the downloaded file.
        """
        dest = Path(dest) if dest else Path.cwd() / Path(key).name

        if dest.is_dir():
            dest = dest / Path(key).name

        dest.parent.mkdir(parents=True, exist_ok=True)

        self._client.download_file(self.bucket, key, str(dest))
        return dest.resolve()

    def write_object(
        self,
        key: str,
        source: str | Path | bytes,
        content_type: str = "application/octet-stream",
        extra_args: dict | None = None,
    ) -> str:
        """
        Upload a file or raw bytes to the bucket.

        Args:
            key:          The destination S3 object key.
            source:       A file path or raw bytes to upload.
            content_type: MIME type for the object (default: application/octet-stream).
            extra_args:   Optional dict of extra args passed to boto3 (e.g. {"ACL": "public-read"}).

        Returns:
            The S3 key of the uploaded object.
        """
        args = {"ContentType": content_type, **(extra_args or {})}
        try:
            if isinstance(source, bytes):
                print(f"Uploading raw bytes to {key} with content type {content_type}")
                self._client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=source,
                    **args
                )
            else:
                print(
                    f"Uploading file {source} to {key} with content type {content_type}"
                )
                self._client.upload_file(
                    str(Path(source).resolve()),
                    self.bucket,
                    key,
                    ExtraArgs=args
                )
        except Exception as e:
            print(f"Error uploading object to S3: {e}")
            raise e

        return key

    def delete_object(self, key: str) -> None:
        """
        Delete a single object from the bucket.

        Args:
            key: The S3 object key to delete.
        """
        self._client.delete_object(Bucket=self.bucket, Key=key)
