import argparse
import base64
import hashlib
import json
import logging
import sys

import boto3
import botocore

logger = logging.getLogger(__name__)
s3 = boto3.client("s3")

DIST_S3_KEY = "dist/{stage}"
MANIFEST_S3_KEY = "manifest.json"


def get_manifest(bucket):
    try:
        response = s3.get_object(Bucket=bucket, Key=MANIFEST_S3_KEY)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.info("Dist manifest not found in %s bucket", bucket)
            manifest = {}
        else:
            raise
    else:
        manifest_body = response["Body"].read()
        manifest = json.loads(manifest_body)
    return manifest


def add_to_manifest(manifest, stage, dist):
    filebase64sha256 = base64.b64encode(hashlib.sha256(dist).digest()).decode()
    manifest[stage] = {
        "file": DIST_S3_KEY.format(stage=stage),
        "filebase64sha256": filebase64sha256,
    }


def remove_from_manifest(manifest, stage):
    try:
        del manifest[stage]
    except KeyError:
        ValueError(f'Stage "{stage}" not found in manifest')


def put_manifest(bucket, manifest):
    body = json.dumps(manifest).encode()
    s3.put_object(
        Bucket=bucket, Key=MANIFEST_S3_KEY, Body=body, ContentType="application/json",
    )


def delete_dist(bucket, stage):
    s3.delete_object(
        Bucket=bucket, Key=DIST_S3_KEY.format(stage=stage),
    )


def put_dist(bucket, stage, dist):
    s3.put_object(
        Bucket=bucket,
        Key=DIST_S3_KEY.format(stage=stage),
        Body=dist,
        ContentType="application/zip",
    )


def main(args=None):
    """Deploy build do s3 bucket.

    The ARGS parameter lets you specify the argument list directly.
    Omitting ARGS (or setting it to None) works as for argparse, using
    sys.argv[1:] as the argument list.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "s3_bucket", help="Bucket name to which the distribution will be uploaded."
    )
    parser.add_argument(
        "stage_name",
        help="Deployment stage name. App will be uploaded under dist/{stage_name} key.",
    )
    parser.add_argument(
        "--dist",
        nargs="?",
        type=argparse.FileType("rb"),
        default=sys.stdin,
        const=False,
        help="Distribution file. Can also be supplied on stdin.",
    )
    parser.add_argument("--destroy", action="store_true")

    args = parser.parse_args(args)

    manifest = get_manifest(args.s3_bucket)
    if args.destroy:
        remove_from_manifest(manifest, args.stage_name)
        put_manifest(args.s3_bucket, manifest)
        delete_dist(args.s3_bucket, args.stage_name)
    else:
        dist = args.dist.read()
        put_dist(args.s3_bucket, args.stage_name, dist)
        add_to_manifest(manifest, args.stage_name, dist)
        put_manifest(args.s3_bucket, manifest)
    args.dist.close()


if __name__ == "__main__":
    main()
