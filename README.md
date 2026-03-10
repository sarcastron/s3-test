# gcp-s3-test

A lightweight CLI tool for testing S3-compatible access to cloud storage buckets. Built primarily for verifying GCP (Google Cloud Storage) HMAC credentials and bucket permissions via the S3 interoperability API, though it works with any S3-compatible endpoint (AWS, MinIO, etc.).

## What it does

Runs a sequence of operations against a target bucket to verify that your credentials have the expected permissions:

1. Lists objects in the bucket
2. Uploads a small inline text file (`sample.txt`)
3. Uploads a local file (`permissions_instructions.md`)
4. Lists objects again to confirm the uploads
5. Deletes the uploaded `sample.txt`
6. Lists objects a final time to confirm deletion

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) for environment and package management

## Setup

```bash
# Clone the repo and enter the directory
git clone <repo-url>
cd gcp-s3-test

# Create a virtual environment and install dependencies
uv sync
```

## Configuration

All configuration is provided via environment variables:

| Variable | Required | Description |
|---|---|---|
| `S3_BUCKET` | Yes | Name of the bucket to test against |
| `S3_ACCESS_KEY` | Yes | HMAC access key (GCS) or AWS access key ID |
| `S3_HMAC_SECRET` | Yes | HMAC secret (GCS) or AWS secret access key |
| `S3_ENDPOINT_URL` | Yes | S3-compatible endpoint URL (e.g. `https://storage.googleapis.com`) |
| `S3_REGION` | No | Region name (defaults to `us-central1`) |

For GCS, generate HMAC keys in the [Google Cloud Console](https://console.cloud.google.com/storage/settings;tab=interoperability) under **Cloud Storage > Settings > Interoperability**.

You can export variables in your shell or use a `.env` file loaded by your shell before running.

For convenience you can copy the `.env.dist` and set the values.

## Usage

```bash
# Activate the virtual environment (if not already active)
source .venv/bin/activate

# Set required environment variables
export S3_BUCKET="your-bucket-name"
export S3_ACCESS_KEY="your-access-key"
export S3_HMAC_SECRET="your-hmac-secret"
export S3_ENDPOINT_URL="https://storage.googleapis.com"
export S3_REGION="us-central1"  # optional

# Run the test
python main.py
```

## Project structure

```
main.py                       # Entry point — runs the permission test sequence
services/
    test_s3_client.py         # S3 client wrapper (boto3-based, GCS-compatible)
permissions_instructions.md   # Sample file uploaded during the test run
pyproject.toml
```
