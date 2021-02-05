FROM python:3.7-slim-buster

ENV PYTHONDONTWRITEBYTECODE True
ENV PYTHONUNBUFFERED True

ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD . /app

ENV PYTHONPATH=${PYTHONPATH}:.

ENTRYPOINT ["python", "nck/entrypoint.py"]
