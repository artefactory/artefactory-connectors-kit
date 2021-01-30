FROM python:3.7

# Install Unix packages
RUN apt-get update && apt-get install -y \
    supervisor \
    cron \
    nano \
    git \
    build-essential \
    unzip \
    libaio-dev \
    && mkdir -p /opt/data/api

RUN mkdir /app

# Copy code
ADD . /app/
RUN chmod -R 0644 /app
WORKDIR /app/
ENV PYTHONPATH=${PYTHONPATH}:.

RUN python setup.py install

ENTRYPOINT ["nckrun"]
