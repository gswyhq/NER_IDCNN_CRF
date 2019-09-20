FROM tensorflow/tensorflow:1.13.1-py3

# docker run --rm -it -v $PWD:/ner -w /ner -p 8000:8000 -e LANG=C.UTF-8 -e TZ=CST-8 tensorflow/tensorflow:1.13.1-py3 /bin/bash

# 更改为国内源
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak

RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial main" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial main" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial-updates main" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates main" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial universe" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial universe" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial-updates universe" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates universe" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial-security main" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main" >> /etc/apt/sources.list
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ xenial-security universe" >> /etc/apt/sources.list
RUN echo "deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security universe" >> /etc/apt/sources.list

RUN apt-get update && apt-get -y install vim git curl nginx

ENV LANG C.UTF-8
ENV LANGUAGE C:zh
ENV LC_ALL C.UTF-8
ENV TZ CST-8

ENV MYDIR /ner

WORKDIR $MYDIR

COPY . $MYDIR/

RUN pip3 install git+https://github.com/Supervisor/supervisor.git

RUN cd $MYDIR && pip3 install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com

RUN git config --global core.quotepath false && \
    git config --global log.date iso8601 && \
    git config --global credential.helper store

#RUN mkdir /var/log/supervisor && \
#    mkdir -p /etc/supervisor/conf.d && \
#    echo_supervisord_conf > /etc/supervisor/supervisord.conf && \
#    echo "[include]" >> /etc/supervisor/supervisord.conf && \
#    echo "files = /etc/supervisor/conf.d/*.conf" >> /etc/supervisor/supervisord.conf
#
#RUN echo 'if [ "$color_prompt" = yes ]; then' >> ~/.bashrc
#RUN echo "    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '" >> ~/.bashrc
#RUN echo "else" >> ~/.bashrc
#RUN echo "    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '" >> ~/.bashrc
#RUN echo "fi" >> ~/.bashrc

RUN echo "alias date='date +\"%Y-%m-%d %H:%M:%S\"'" >> ~/.bashrc
RUN echo "export TERM=xterm" >> ~/.bashrc
RUN echo "source /usr/share/bash-completion/completions/git" >> ~/.bashrc
RUN echo "export PATH=/bin/bash:$PATH" >> ~/.bashrc

EXPOSE 8000

#ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/bin/bash"]

# docker build -t ner:20180905 -f Dockerfile .

