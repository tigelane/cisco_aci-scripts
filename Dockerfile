FROM ubuntu:latest

MAINTAINER Tige Phillips <tige@tigelane.com>

RUN apt-get update --fix-missing
RUN apt-get -y upgrade

###########
# PYTHON 
###########
<<<<<<< HEAD
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-setuptools
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-dev libffi-dev libssl-dev
=======
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python2.7 \
													  python-setuptools \
													  python-pip
>>>>>>> 5620d301593f8250f70035c47fadd77f9bc66e8a

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
<<<<<<< HEAD
WORKDIR /
=======
>>>>>>> 5620d301593f8250f70035c47fadd77f9bc66e8a
RUN pip install tweepy

###########
#  Adding the scripts from this repository
###########
VOLUME /usr/local/bin
ADD *.py /usr/local/bin/

WORKDIR /usr/local/bin

# By default when this container runs start a console.
<<<<<<< HEAD
CMD ["-v", "/usr/local/bin"]
=======
CMD /bin/bash
>>>>>>> 5620d301593f8250f70035c47fadd77f9bc66e8a
