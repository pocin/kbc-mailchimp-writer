FROM quay.io/keboola/base-python:3.5.2-c

MAINTAINER Robin robin@keboola.com

RUN pip install --no-cache-dir --ignore-installed \
    mailchimp3 \
		pytest \
		requests \
    pandas \
    && pip install --upgrade --no-cache-dir --ignore-installed git+git://github.com/keboola/python-docker-application.git@1.3.0

# prepare the container
WORKDIR /home
