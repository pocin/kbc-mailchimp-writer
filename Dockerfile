FROM quay.io/keboola/docker-custom-python:1.3.0

MAINTAINER Robin robin@keboola.com

RUN pip install --no-cache-dir --ignore-installed \
    mailchimp3 \
		pytest \
		requests \
    pandas \
    pytest-cov\
    && pip install --upgrade --no-cache-dir --ignore-installed git+git://github.com/keboola/python-docker-application.git@2.0.0

# prepare the container
WORKDIR /home
