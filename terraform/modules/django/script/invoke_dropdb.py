import argparse
import base64
import datetime
import hashlib
import hmac
import json
import os
import sys
import urllib.parse
import urllib.request


def sign(key, msg):
    """
    Key derivation functions. See:
    http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    """
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def getSignatureKey(key, date_stamp, regionName, serviceName):
    """
    Key derivation functions. See:
    http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    """
    kDate = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "aws4_request")
    return kSigning


def create_headers(access_key, secret_key, region, function_name, request_parameters):
    # ************* REQUEST VALUES *************
    method = "POST"
    service = "lambda"
    host = "lambda.%s.amazonaws.com" % region
    # POST requests use a content type header. For Lambda,
    # the content is JSON.
    content_type = "application/x-amz-json-1.0"

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")  # Date w/o time, used in credential scope

    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

    # Step 1 is to define the verb (GET, POST, etc.)--already done.

    # Step 2: Create canonical URI--the part of the URI from domain to query
    # string (use '/' if no path)
    canonical_uri = "/2015-03-31/functions/%s/invocations" % function_name

    ## Step 3: Create the canonical query string. In this example, request
    # parameters are passed in the body of the request and the query string
    # is blank.
    canonical_querystring = ""

    # Step 4: Create the canonical headers. Header names must be trimmed
    # and lowercase, and sorted in code point order from low to high.
    # Note that there is a trailing \n.
    canonical_headers = (
        "content-type:"
        + content_type
        + "\n"
        + "host:"
        + host
        + "\n"
        + "x-amz-date:"
        + amz_date
        + "\n"
    )

    # Step 5: Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    # Note: The request can include any headers; canonical_headers and
    # signed_headers include those that you want to be included in the
    # hash of the request. "Host" and "x-amz-date" are always required.
    signed_headers = "content-type;host;x-amz-date"

    # Step 6: Create payload hash. In this example, the payload (body of
    # the request) contains the request parameters.
    payload_hash = hashlib.sha256(request_parameters.encode("utf-8")).hexdigest()

    # Step 7: Combine elements to create canonical request
    canonical_request = (
        method
        + "\n"
        + canonical_uri
        + "\n"
        + canonical_querystring
        + "\n"
        + canonical_headers
        + "\n"
        + signed_headers
        + "\n"
        + payload_hash
    )

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    # Match the algorithm to the hashing algorithm you use, either SHA-1 or
    # SHA-256 (recommended)
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = date_stamp + "/" + region + "/" + service + "/" + "aws4_request"
    string_to_sign = (
        algorithm
        + "\n"
        + amz_date
        + "\n"
        + credential_scope
        + "\n"
        + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    )

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    # Create the signing key using the function defined above.
    signing_key = getSignatureKey(secret_key, date_stamp, region, service)

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(
        signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    # Put the signature information in a header named Authorization.
    authorization_header = (
        algorithm
        + " "
        + "Credential="
        + access_key
        + "/"
        + credential_scope
        + ", "
        + "SignedHeaders="
        + signed_headers
        + ", "
        + "Signature="
        + signature
    )

    # For DynamoDB, the request can include any headers, but MUST include "host", "x-amz-date",
    # "x-amz-target", "content-type", and "Authorization". Except for the authorization
    # header, the headers must be included in the canonical_headers and signed_headers values, as
    # noted earlier. Order here is not significant.
    # # Python note: The 'host' header is added automatically by the Python 'requests' library.
    return {
        "Content-Type": content_type,
        "Host": host,
        "X-Amz-Date": amz_date,
        "Authorization": authorization_header,
    }


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("function_name")
    parser.add_argument("db_name")
    parser.add_argument("--access_key")
    parser.add_argument("--secret_key")
    parser.add_argument("--region")

    args = parser.parse_args(args)

    access_key = args.access_key or os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = args.secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = args.secret_key or os.environ.get("AWS_DEFAULT_REGION")
    if not (access_key and secret_key and region):
        raise ValueError("Could not find aws credentials")

    endpoint = "https://lambda.%s.amazonaws.com/2015-03-31/functions/%s/invocations" % (
        region,
        args.function_name,
    )
    data_dict = {"manage": ["dropdb", args.db_name]}
    data = json.dumps(data_dict)
    headers = create_headers(access_key, secret_key, region, args.function_name, data)
    request = urllib.request.Request(
        endpoint, data=data.encode("ascii"), headers=headers
    )
    try:
        with urllib.request.urlopen(request) as response:
            content = response.read()
            print(content)
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())


if __name__ == "__main__":
    main()
