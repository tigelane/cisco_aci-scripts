FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update --fix-missing
RUN apt-get -y upgrade

###########
# PYTHON 
###########
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-setuptools
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-dev libffi-dev libssl-dev

###########
# GIT 
###########
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git

###########
# ACI Toolkit Install
###########
RUN git clone https://github.com/datacenter/acitoolkit.git
WORKDIR acitoolkit
RUN python setup.py install

###########
# Tweepy
###########
WORKDIR /
RUN pip install tweepy

###########
#  Adding the scripts from this repository
###########
VOLUME /usr/local/bin
ADD *.py /usr/local/bin/

WORKDIR /usr/local/bin

# By default when this container runs start a console.
CMD ["-v", "/usr/local/bin"]
