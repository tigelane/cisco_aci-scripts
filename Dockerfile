FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update --fix-missing
RUN apt-get -y upgrade

###########
# apt-get 
###########
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7 \
													  python-setuptools \
													  python-pip
													  git
													  
###########
# ACI Toolkit Install
###########
RUN git clone https://github.com/datacenter/acitoolkit.git
RUN python acitoolkit/setup.py install

###########
# Tweepy
###########
RUN pip install tweepy

###########
#  Adding the scripts from this repository
###########
VOLUME /usr/local/bin
ADD acitoolkit/*.py /usr/local/bin/

WORKDIR /usr/local/bin

# By default when this container runs start a console.
CMD ["-v", "/usr/local/bin"]

