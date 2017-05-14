#!/bin/sh
VERSION=0.1.0
IMAGE="pocin/kbc-mailchimp-writer"
docker tag ${IMAGE}:${VERSION}
docker tag ${IMAGE}:latest
docker push ${IMAGE}:${VERSION}
docker push ${IMAGE}:latest
