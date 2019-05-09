FROM ubuntu:18.04

ENV LANGUAGE C.UTF-8
ENV LC_CTYPE C.UTF-8
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

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

# Oracle Dependencies
ADD ./docker-depedencies /opt/data

WORKDIR /opt/data

ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

ENV OCI_HOME=/opt/oracle/instantclient
ENV OCI_LIB_DIR=/opt/oracle/instantclient
ENV OCI_INCLUDE_DIR=/opt/oracle/instantclient/sdk/include

# Install Oracle
RUN mkdir /opt/oracle
RUN chmod +x /opt/data/install.sh
RUN /opt/data/install.sh

# Install Python and PIP
RUN apt-get update \
  && apt-get install -y python2.7 python-pip python2.7-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip install --upgrade pip 

RUN mkdir /nautilus-connectors-kit

# Install dependencies
ADD requirements.txt /nautilus-connectors-kit/requirements.txt
RUN pip install -r /nautilus-connectors-kit/requirements.txt

# Copy code
ADD . /nautilus-connectors-kit/
RUN chmod -R 0644 /nautilus-connectors-kit
ENV PYTHONPATH /nautilus-connectors-kit

ARG ENV
ENV ENV=$ENV

ENTRYPOINT ["python", "/nautilus-connectors-kit/bin/app.py"]
