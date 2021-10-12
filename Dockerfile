FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE True
ENV PYTHONUNBUFFERED True

ADD requirements.txt .

RUN apt update -y
RUN apt install -y build-essential

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt --use-deprecated=legacy-resolver

WORKDIR /app
ADD . /app

ENV PYTHONPATH=${PYTHONPATH}:.

ENTRYPOINT ["python", "ack/entrypoints/cli/main.py"]
