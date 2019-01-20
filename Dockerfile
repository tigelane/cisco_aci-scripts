FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update
RUN apt-get -y upgrade

#
# Foundation
############
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install graphviz-dev pkg-config
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git vim-tiny
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python python-setuptools python-pip
RUN DEBIAN_FRONTEND=noninteractive pip install --upgrade pip

#
# ACI Toolkit Install
#####################
WORKDIR /opt
RUN git clone https://github.com/datacenter/acitoolkit.git
COPY ./acitoolkit-setup.py ./acitoolkit/setup.py
WORKDIR /opt/acitoolkit
RUN python setup.py install

#
# Cisco ACI Scripts
###################
WORKDIR /opt
RUN git clone https://github.com/tigelane/cisco_aci-scripts.git

###########
# Tweepy
###########
RUN pip install tweepy
