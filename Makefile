test:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ tests

bash:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ bash
