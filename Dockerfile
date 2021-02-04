FROM python:3.7-slim-buster

ENV PYTHONDONTWRITEBYTECODE True
ENV PYTHONUNBUFFERED True

WORKDIR /app
ADD . /app
RUN python -m pip install -r requirements.txt
ENV PYTHONPATH=${PYTHONPATH}:.

ENTRYPOINT ["python", "nck/entrypoint.py"]
