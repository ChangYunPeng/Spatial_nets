# Pull base image.

FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.5
RUN apt-get update

RUN apt-get install -y build-essential python3.5 python3.5-dev python3-pip python3.5-venv
RUN apt-get install -y git

# update pip
RUN python3.5 -m pip install pip --upgrade
RUN python3.5 -m pip install wheel
RUN python3.5 -m pip install pip -U
RUN python3.5 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3.5 -m pip install numpy \
        enum34 \
        futures \
        pathlib \
        tifffile \
        requests \
        opencv-python \
        pillow \
        scipy \
        http://download.pytorch.org/whl/cpu/torch-0.4.1-cp35-cp35m-linux_x86_64.whl \
        torchvision \
        rasterio
RUN apt-get update && apt-get install -y libsm6 libxext6 libgtk2.0-dev

# RUN echo "PYTHONPATH=/usr/lib/python2.7" >> ~/.bashrc

WORKDIR "/root/workdir"

ENV LANG C.UTF-8

COPY ./mod-ZJ /root/workdir/python
# RUN chmod 777 entrypoint.sh /root/workdir/python/convert.py --lonlat2pxpy 1
CMD python3 /root/workdir/python/CNN_server.py --ip_port 192.168.88.168:8076 --port 7798
# --ip_port  --port
# EXPOSE 8099
# python3 /root/workdir/python/TEST_SpatialNets.py
# ENTRYPOINT ["java","-jar","/geoclouds.jar"]
