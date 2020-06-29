FROM lambci/lambda:build-python3.8
ENV PYTHONUNBUFFERED 1
COPY requirements/prod.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
COPY . /var/task
