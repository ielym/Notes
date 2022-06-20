From ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

WORKDIR /home

RUN apt-get -y update
RUN apt-get install -y cmake
RUN apt-get install -y wget
RUN apt-get -y install vim
RUN apt-get -y install libbz2-dev
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-dev
RUN apt-get install -y libsasl2-dev python3-dev libldap2-dev libssl-dev

# install python3.x.x
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt install build-essential -y
RUN apt install libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev -y
RUN apt install zlib1g-dev -y
RUN apt install wget -y
RUN apt install openssl -y
RUN apt install curl -y
RUN apt install libsqlite3-dev -y
RUN wget https://www.python.org/ftp/python/3.7.5/Python-3.7.5.tgz
RUN tar -xvf Python-3.7.5.tgz
WORKDIR  /home/Python-3.7.5
RUN ls
RUN ./configure --enable-loadable-sqlite-extensions
RUN make
RUN make install
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/local/bin/pip3 /usr/bin/pip
RUN ln -s /usr/local/bin/python3 /usr/bin/python



# install python packages
# ============================================================================
# prepare environments
RUN apt-get -y update
RUN apt-get install -y liblzma-dev
# pip install
WORKDIR /home
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
# ============================================================================

WORKDIR  /home/Python-3.7.5
RUN ./configure
RUN make && make install

WORKDIR /home
