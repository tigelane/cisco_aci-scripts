FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update --fix-missing
RUN apt-get -y upgrade

###########
# apt-get 
###########
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-setuptools
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git
													  
###########
# ACI Toolkit Install
###########
RUN git clone https://github.com/datacenter/acitoolkit.git
WORKDIR /acitoolkit
RUN python setup.py install
WORKDIR /

###########
# Cisco ACI Scripts
###########
RUN git clone https://github.com/tigelane/cisco_aci-scripts.git

###########
# Tweepy
###########
RUN pip install tweepy


