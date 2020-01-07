FROM python:3.7.6-slim-buster

WORKDIR /root

# install system dependencies and nice-to-haves
RUN apt-get update && apt-get -y install \
    curl \
    htop \
    less \
    net-tools \
    procps \
    screen \
    telnet \
    vim \
    && apt-get clean \
    && rm -Rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install -U pip
ADD requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

# install audioserver package
ADD setup.py /root/audioserver/setup.py
ADD audioserver /root/audioserver/audioserver
RUN cd /root/audioserver \
    && pip install .

EXPOSE 5000

RUN ["audioserver", "--port", "5000", "--path", "/root/files"]