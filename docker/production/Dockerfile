FROM ubuntu:latest
MAINTAINER Paweł Jastrzębski <pawel.jastrzebski@stxnext.pl>

# Recipe expect to find:
# - lunch-app directory that is clone of application repository
# - buildout.cfg file that will replace default one

# Prepare base system
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y curl locales

# Configure system locales
RUN echo 'en_US.UTF-8 UTF-8\npl_PL.UTF-8 UTF-8' > /etc/locale.gen && locale-gen
ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install dependencies
RUN apt-get install -y build-essential python3 python3-dev libpq-dev libpcre3 libpcre3-dev
RUN curl -sL https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install uwsgi

# Cleanup and system configuration
RUN echo "Europe/Warsaw" > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get clean -y && apt-get autoclean -y && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Building
ADD lunch-app /root/lunch-app
ADD buildout.cfg /root/lunch-app/buildout.cfg
WORKDIR /root/lunch-app
RUN mkdir /root/lunch-app/download-cache && python3 bootstrap-buildout.py && ./bin/buildout -vN && ln -s /usr/local/bin/uwsgi /root/lunch-app/bin/uwsgi
RUN ./bin/flask-ctl db_migrate upgrade
CMD ./bin/flask-ctl serve fg
EXPOSE 8080
