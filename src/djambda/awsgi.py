import io

import awsgi
from django.core import management

from .wsgi import application


def lambda_handler(event, context):
    if "manage" in event:
        output = io.StringIO()
        management.call_command(*event["manage"].split(" "), stdout=output)
        return {"output": output.getvalue()}
    else:
        return awsgi.response(application, event, context)
