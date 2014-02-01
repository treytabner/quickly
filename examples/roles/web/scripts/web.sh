#!/bin/sh

export DEBIAN_FRONTEND=noninteractive

apt-get -y install ssl-cert nginx uwsgi uwsgi-plugin-python

mkdir -p /etc/uwsgi/apps-enabled
for i in /etc/uwsgi/apps-available/*.ini ; do
    ln -sf $i /etc/uwsgi/apps-enabled
done
