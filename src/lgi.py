import json
import sys
from io import BytesIO, StringIO
from typing import Any, Dict, List
from wsgiref.headers import Headers

import django
from django.conf import settings
from django.core import management, signals
from django.core.handlers import base
from django.http import HttpRequest, QueryDict, parse_cookie
from django.urls import set_script_prefix
from django.utils.functional import cached_property

_default_route_key = "$default"


class LGIRequest(HttpRequest):
    def __init__(self, payload):
        self._read_started = False
        self.resolver_match = None
        script_name = (
            "" if payload["routeKey"] == _default_route_key else payload["routeKey"]
        )
        self.path_info = payload["requestContext"]["http"]["path"]
        self.path = "%s/%s" % (
            script_name.rstrip("/"),
            self.path_info.replace("/", "", 1),
        )
        self.method = payload["requestContext"]["http"]["method"]

        self.META = {
            "REQUEST_METHOD": self.method,
            "QUERY_STRING": payload["rawQueryString"],
            "SCRIPT_NAME": script_name,
            "PATH_INFO": self.path_info,
            "REMOTE_ADDR": payload["requestContext"]["http"]["sourceIp"],
            "REMOTE_HOST": payload["requestContext"]["http"]["sourceIp"],
            "SERVER_NAME": payload["requestContext"]["domainName"],
            "SERVER_PORT": "443",
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
        }
        for name, value in payload["headers"].items():
            corrected_name = name.replace("-", "_").upper()
            if corrected_name not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                corrected_name = f"HTTP_{corrected_name}"
            # Duplicate query strings are combined with commas
            self.META[corrected_name] = value
        self._set_content_type_params(self.META)

    def _get_scheme(self):
        # all of the APIs created with Amazon API Gateway expose HTTPS endpoints only
        return "https"

    @cached_property
    def GET(self):
        return QueryDict(self.META["QUERY_STRING"])

    def _get_post(self):
        if not hasattr(self, "_post"):
            self._load_post_and_files()
        return self._post

    def _set_post(self):
        self._post = post

    POST = property(_get_post, _set_post)

    @property
    def FILES(self):
        if not hasattr(self, "_files"):
            self._load_post_and_files()
        return self._files

    @cached_property
    def COOKIES(self):
        return parse_cookie(self.META.get("HTTP_COOKIE", ""))


class LGIHandler(base.BaseHandler):
    request_class = LGIRequest

    def __init__(self):
        super().__init__()
        self.load_middleware()

    def __call__(self, payload, context):
        print(payload, context)
        # handle manage.py
        if "manage" in payload:
            output = StringIO()
            management.call_command(*payload["manage"], stdout=output)
            return {"output": output.getvalue()}

        # handle api gateway
        version = payload["version"]
        if version != "2.0":
            raise ValueError(f"{version} format version is not supported")

        set_script_prefix(self.get_script_prefix(payload))
        signals.request_started.send(sender=self.__class__, payload=payload)
        request = self.request_class(payload)
        response = self.get_response(request)

        response._handler_class = self.__class__

        return json.dumps(
            {
                "body": response.content.decode(),
                "headers": list(response.items()),
                "statusCode": response.status_code,
                "isBase64Encoded": False,
                "cookies": list(response.cookies.values()),
            }
        )

    def get_script_prefix(self, payload):
        if settings.FORCE_SCRIPT_NAME:
            return settings.FORCE_SCRIPT_NAME
        return "" if payload["routeKey"] == _default_route_key else payload["routeKey"]


def get_lgi_application():
    django.setup(set_prefix=False)
    return LGIHandler()
