test:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ tests
testvv:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ testsvv

testcov:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ testcov

bash:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ bash

build:
	docker build -t pocin/kbc-mailchimp-writer .
