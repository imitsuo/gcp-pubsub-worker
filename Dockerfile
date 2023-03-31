FROM python:3.8-slim-buster

ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# To install github private repositories
RUN apt-get update && apt-get install -y git


RUN mkdir api
WORKDIR /api

RUN mkdir app

# Install dependencies
COPY requirements.txt app/
RUN pip install -r app/requirements.txt

# copy project
COPY app app

ENV TZ="UTC"

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8  --timeout 0 app.main:app
