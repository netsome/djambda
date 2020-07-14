FROM python:3-alpine
RUN pip install --no-cache-dir boto3 requests
COPY script /script/
