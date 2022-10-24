FROM python:3.6.5

# 1.设置工作目录
ENV BASE_DIR="/home"
WORKDIR $BASE_DIR

# 2.安装基础包
RUN apt-get -y  update \
    && apt-get -y install git wget gcc make \
    perl m4 flex bison \
    libxml2-dev libxslt-dev \
    python3-setuptools python3-dev libssl-dev libgmp-dev libmpc-dev python3-pip

## 3.定义脚本参数，动态执行
#ENV P hbbft
#ENV N 4
#ENV f 1
#ENV B 256
#ENV K 1
#ENV id 0

RUN python -m pip install --upgrade pip

# 4.安装基础包
RUN pip3 install pyparsing==2.4.6
RUN pip3 install --upgrade setuptools && pip3 install --upgrade greenlet
RUN pip3 install PySocks ecdsa zfec gipc pycrypto numpy coincurve

# 5.编译安装GMP
RUN wget --no-check-certificate https://gmplib.org/download/gmp/gmp-5.1.3.tar.bz2
RUN tar -jxvf gmp-5.1.3.tar.bz2 && cd gmp-5.1.3 &&./configure && make && make install && cd ..

# 6.编译安装PBC
RUN wget --no-check-certificate https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz \
    && tar -zxvf pbc-0.5.14.tar.gz \
    && cd pbc-0.5.14 && ./configure \
    && make && make install && cd .. \

RUN export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/lib
RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
ENV LIBRARY_PATH /usr/local/lib
ENV LD_LIBRARY_PATH /usr/local/lib

# 7.编译安装Charm-Crypto，git下载报错
#RUN git clone -b dev https://github.com/JHUISI/charm.git \
#    && cd charm && ./configure.sh && make && make install && cd .. \
ADD charm charm
RUN chmod +x charm
RUN cd charm && bash ./configure.sh && make && make install && cd ..

# 8.复制源码到工作目录
ADD . $BASE_DIR/

#RUN pip install --upgrade pip
#RUN pip install -e .[dev]

# 9.启动脚本
#RUN chmod +x run_socket_network.sh
#CMD sh run_socket_network.sh

# 10.启动镜像后进入命令行，手动运行脚本（调试用）
#CMD ["/bin/bash"]

