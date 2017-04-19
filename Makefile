test:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ tests
testvv:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ testsvv
bash:
	docker-compose run --rm -e KBC_DATADIR=/src/tests/data/ bash
