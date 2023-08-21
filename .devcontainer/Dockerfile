FROM python:3.8
ARG DEBIAN_FRONTEND=noninteractive
RUN echo 'start build'
RUN LC_ALL=C.UTF-8
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

RUN pip3 install --user flit -i https://mirrors.ustc.edu.cn/pypi/web/simple/
RUN pip3 install --user py_dev_support -i https://mirrors.ustc.edu.cn/pypi/web/simple/
ENV PATH="$PATH:/root/.local/bin"

ENTRYPOINT tail -f /dev/null