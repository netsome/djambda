# syntax = docker/dockerfile:1.0-experimental
FROM lambci/lambda:build-python3.8
ENV PYTHONUNBUFFERED 1
COPY requirements/dev.txt /code/requirements.txt
RUN --mount=dst=/root/.cache/pip,type=cache pip install -r /code/requirements.txt
COPY . /var/task
