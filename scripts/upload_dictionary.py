import boto3
import json
import logging
import sys
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

s3_client = boto3.client("s3")


def get_dict_version(dict_file_path):
    """
    Extracts the dictionary version from the provided JSON/YAML combo settings.

    Args:
        dict_file_path (str): Path to the dictionary file.

    Returns:
        str: Dictionary version.
    """
    with open(dict_file_path, "r", encoding="utf-8") as f:
        dict_data = json.load(f)
    return dict_data.get("_settings.yaml", {}).get("_dict_version", None)


def upload_dict_to_s3(dict_file_path, s3_target_uri, dict_version):
    """
    Uploads a dictionary file to S3 with metadata.

    Args:
        dict_file_path (str): Local dictionary path.
        s3_target_uri (str): URI like s3://bucket/key.
        dict_version (str): Dictionary version string.

    Returns:
        bool: True on success, False otherwise.
    """
    if not s3_target_uri.startswith("s3://"):
        logger.error(f"Invalid S3 URI: {s3_target_uri}")
        return False

    try:
        s3_path = s3_target_uri[len("s3://") :]
        if "/" not in s3_path:
            logger.error(f"S3 URI missing key: {s3_target_uri}")
            return False
        bucket, key = s3_path.split("/", 1)
        # Set S3 metadata key to "version" instead of "dict_version"
        extra_args = {"Metadata": {"version": dict_version or "unknown"}}
        s3_client.upload_file(dict_file_path, bucket, key, ExtraArgs=extra_args)
        logger.info(
            f"Successfully uploaded '{dict_file_path}' (version: {dict_version}) to {s3_target_uri}"
        )
        return True
    except ClientError as e:
        logger.error(f"Failed to upload file to {s3_target_uri}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {e}")
        return False


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python upload_dictionary.py <local_file_path> <s3_uri>",
            file=sys.stderr,
        )
        sys.exit(1)

    local_file_path = sys.argv[1]
    s3_uri = sys.argv[2]
    dict_version = get_dict_version(local_file_path)
    if dict_version is None:
        logger.error(f"Could not determine dictionary version from {local_file_path}")
        sys.exit(1)

    success = upload_dict_to_s3(local_file_path, s3_uri, dict_version)
    if not success:
        sys.exit(1)
    # You may add a completion message if desired


if __name__ == "__main__":
    main()
