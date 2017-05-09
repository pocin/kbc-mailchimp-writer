FROM quay.io/keboola/docker-custom-python:1.3.0

MAINTAINER Robin robin@keboola.com

RUN pip install --no-cache-dir --ignore-installed \
    mailchimp3==2.0.11 \
		pytest==3.0.7\
		requests==2.13.0\
    pytest-cov==2.4.0\
    && pip install --upgrade --no-cache-dir --ignore-installed git+git://github.com/keboola/python-docker-application.git@2.0.0

ENTRYPOINT python /src/main.py
# prepare the container
WORKDIR /home
