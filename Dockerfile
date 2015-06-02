FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update
RUN apt-get -y upgrade

###########
# PYTHON 
###########
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7 python-setuptools python-pip

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
#  Adding the scripts from this repository
###########
ADD *.py /usr/local/bin/