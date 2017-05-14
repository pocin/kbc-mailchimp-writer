VERSION=0.1.0
IMAGE="pocin/kbc-mailchimp-writer"

test:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ tests
testvv:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ testsvv

testcov:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ testcov

bash:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ bash

build:
	echo "Building ${IMAGE}:${VERSION}"
	docker build -t ${IMAGE}:${VERSION} -t ${IMAGE}:latest .

deploy:
	echo "Pusing to dockerhub"
	docker push ${IMAGE}:${VERSION}
	docker push ${IMAGE}:latest
