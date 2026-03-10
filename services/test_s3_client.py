"""A clean, highly-compatible S3 client for testing with GCS."""

import boto3
from botocore.client import Config, ClientError
from pathlib import Path


class TestS3Client:
    """
    S3 client implementation optimized for GCS Interoperability.
    """

    def __init__(
        self,
        bucket: str,
        access_key: str,
        hmac_secret: str,
        endpoint_url: str,
        region: str,
    ) -> None:
        self.bucket = bucket

        # GCS S3 Interoperability often works more reliably with V2 signatures ('s3')
        # than with V4 ('s3v4') for PUT operations involving raw bytes.
        self._client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=hmac_secret,
            endpoint_url=endpoint_url,
            region_name=region,
            config=Config(
                signature_version="s3",  # Use V2 signature for maximum compatibility
                s3={"addressing_style": "path"},
            ),
        )

    def list_objects(self, prefix: str = "", max_keys: int = 10) -> list:
        """Simple list operation."""
        try:
            response = self._client.list_objects_v2(
                Bucket=self.bucket, Prefix=prefix, MaxKeys=max_keys
            )
            return response.get("Contents", [])
        except Exception as e:
            print(f"List failed: {e}")
            raise e

    def write_object(
        self,
        key: str,
        source: str | Path | bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Uploads an object using put_object.
        """
        if isinstance(source, (str, Path)):
            with open(source, "rb") as f:
                body = f.read()
        else:
            body = source

        put_args = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": body,
            "ContentLength": len(body),
            "ContentType": content_type,
        }

        try:
            self._client.put_object(**put_args)
            return key
        except ClientError as e:
            print(f"Upload failed with ClientError: {e}")
            # Printing the full response can help diagnose GCS-specific errors
            if "Error" in e.response:
                print(f"GCS Error Code: {e.response['Error'].get('Code')}")
                print(f"GCS Error Message: {e.response['Error'].get('Message')}")
            raise e
        except Exception as e:
            print(f"Upload failed with unexpected error: {e}")
            raise e

    def download_object(self, key: str, dest: str | Path) -> Path:
        """Download an object to a local path."""
        dest_path = Path(dest)
        self._client.download_file(self.bucket, key, str(dest_path))
        return dest_path
