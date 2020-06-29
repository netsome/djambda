import io
import json
import os
import tempfile
import unittest
import unittest.mock

import boto3
import botocore
import botocore.stub
import deploy


class TestDeployCli(unittest.TestCase):
    s3_bucket = "s3_bucket"
    stage_name = "stage_name"

    def test_create(self):
        with tempfile.NamedTemporaryFile(delete=False) as dist_file:
            content = b"dist"
            dist_file.write(content)

        stubber = botocore.stub.Stubber(deploy.s3)
        stubber.add_client_error("get_object", "NoSuchKey")
        stubber.add_response(
            "put_object",
            {},
            {
                "Body": content,
                "Bucket": self.s3_bucket,
                "ContentType": "application/zip",
                "Key": f"dist/{self.stage_name}",
            },
        )
        stubber.add_response(
            "put_object",
            {},
            {
                "Body": json.dumps(
                    {
                        self.stage_name: {
                            "file": f"dist/{self.stage_name}",
                            "filebase64sha256": "vK4EFmIbPbQ9jLoeRFSnksevnktyh+UQVu/FohXZWDk=",
                        }
                    }
                ).encode(),
                "Bucket": self.s3_bucket,
                "ContentType": "application/json",
                "Key": f"manifest.json",
            },
        )
        stubber.activate()
        deploy.main([self.s3_bucket, self.stage_name, "--dist", dist_file.name])

        os.unlink(dist_file.name)

    def test_destroy(self):
        pass
