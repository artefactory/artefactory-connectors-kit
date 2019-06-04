FROM python:2.7

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
ADD ./vendor /opt/vendor

WORKDIR /opt/vendor

ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

ENV OCI_HOME=/opt/oracle/instantclient
ENV OCI_LIB_DIR=/opt/oracle/instantclient
ENV OCI_INCLUDE_DIR=/opt/oracle/instantclient/sdk/include

# Install Oracle
RUN mkdir /opt/oracle
RUN chmod +x /opt/vendor/install.sh
RUN /opt/vendor/install.sh

RUN mkdir /app

# Install dependencies
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy code
ADD . /app/
RUN chmod -R 0644 /app
WORKDIR /app/
ENV PYTHONPATH=${PYTHONPATH}:.

ENTRYPOINT ["python", "./bin/app.py"]
