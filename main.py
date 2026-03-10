"""Testing the S3 bucket permission for key"""

import os
from botocore.exceptions import ClientError
from rich import print as rprint
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
            rprint(f"Warning: Environment variable {var_name} is not set.")
            kill_it = True

    if kill_it:
        rprint("Please set the required environment variables and try again.")
        exit(1)

    client = TestS3Client(
        bucket=bucket,
        access_key=access_key,
        hmac_secret=hmac_secret,
        endpoint_url=endpoint_url,
        region=region,
    )
    rprint("Attempting to connect to ", bucket)

    rprint("--- Listing objects in the bucket...")
    list_results = client.list_objects(prefix="", max_keys=10)
    rprint(list_results)

    try:
        print("\n--- Uploading a file")
        key = client.write_object(
            key="sample.txt",
            source=b"Sample text content for permissions instructions.",
        )
        rprint(f"  ├ Uploaded file with key: {key}")

        key = client.write_object(
            key="permissions_instructions.md",
            source="./permissions_instructions.md",
            content_type="text/markdown",
        )
        rprint(f"  ├ Uploaded file with key: {key}")
    except ClientError as e:
        rprint(f"S3 Client Error: {e}")
    except Exception as e:  # pylint: disable=broad-except
        rprint(f"An unexpected error occurred: {e}")

    rprint("\nListing objects after upload the bucket...")
    list_results = client.list_objects(prefix="", max_keys=10)
    rprint(list_results)

    rprint("\n---Deleting uploaded object...")
    try:
        client.delete_object(key="sample.txt")
        rprint("  ├ Objects deleted successfully.")
    except ClientError as e:
        rprint(f"S3 Client Error during deletion: {e}")
    except Exception as e:  # pylint: disable=broad-except
        rprint(f"An unexpected error occurred during deletion: {e}")

    rprint("\n--- Listing objects after deletion the bucket...")
    list_results = client.list_objects(prefix="", max_keys=10)
    rprint(list_results)


if __name__ == "__main__":
    main()
