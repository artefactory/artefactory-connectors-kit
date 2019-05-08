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
    git

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
