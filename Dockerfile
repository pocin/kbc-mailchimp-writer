FROM alpine:3.6

MAINTAINER Robin robin@keboola.com

RUN apk add --no-cache python3 git && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache

RUN pip install --no-cache-dir --ignore-installed \
    mailchimp3==2.0.11 \
		pytest==3.0.7\
		requests==2.13.0\
    pytest-cov==2.4.0\
    && pip install --upgrade --no-cache-dir --ignore-installed git+git://github.com/keboola/python-docker-application.git@2.0.0

COPY . /src/

CMD python -u /src/main.py
# prepare the container
WORKDIR /home
