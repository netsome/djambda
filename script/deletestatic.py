import argparse
import logging

import boto3

logger = logging.getLogger(__name__)
s3 = boto3.resource("s3")


def delete_static(bucket, stage):
    bucket = s3.Bucket(bucket)
    bucket.objects.filter(Prefix=stage).delete()


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("s3_bucket")
    parser.add_argument("stage_name")

    args = parser.parse_args(args)

    delete_static(args.s3_bucket, args.stage_name)


if __name__ == "__main__":
    main()
