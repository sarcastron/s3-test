"""Derp!"""

import os
from services.test_s3_client import TestS3Client


def main():
    """Quick test of the TestS3Client."""
    bucket = os.getenv("S3_BUCKET", None)
    access_key = os.getenv("S3_ACCESS_KEY", None)
    hmac_secret = os.getenv("S3_HMAC_SECRET", None)
    endpoint_url = os.getenv("S3_ENDPOINT_URL", None)
    region = os.getenv("S3_REGION", "us-central1")

    kill_it = False
    for var_name, var_val in [
        ("S3_BUCKET", bucket),
        ("S3_ACCESS_KEY", access_key),
        ("S3_HMAC_SECRET", hmac_secret),
        ("S3_ENDPOINT_URL", endpoint_url),
        ("S3_REGION", region),
    ]:
        if var_val is None:
            print(f"Warning: Environment variable {var_name} is not set.")
            kill_it = True

    if kill_it:
        print("Please set the required environment variables and try again.")
        exit(1)

    client = TestS3Client(
        bucket=bucket,
        access_key=access_key,
        hmac_secret=hmac_secret,
        endpoint_url=endpoint_url,
        region=region,
    )
    print("Attempting to connect to ", bucket)

    print("Listing objects in the bucket...")
    list_results = client.list_objects(prefix="", max_keys=10)
    print(list_results)

    try:
        print("\n Uploading a file")
        key = client.write_object(
            key="sample.txt",
            source=b"Sample text content for permissions instructions.",
        )
        key = client.write_object(
            key="permissions_instructions.md",
            source="./permissions_instructions.md",
            content_type="text/markdown",
        )
        print(f"Uploaded file with key: {key}")
    except Exception as e:
        print(f"Error file: {e}")


if __name__ == "__main__":
    main()
