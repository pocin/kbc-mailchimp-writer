VERSION=0.2.0
IMAGE=pocin/kbc-mailchimp-writer
TESTCOMMAND="docker run --rm -it --entrypoint '/bin/bash' -v `pwd`:/src/ -e KBC_DATADIR='/src/tests/data/' ${IMAGE}:latest /src/run_tests.sh"
test:
	eval $(TESTCOMMAND)

verbosetest:
	eval $(TESTCOMMAND) -vv

testcov:
	$(TESTCOMMAND) --cov-report html  --cov=/src/mcwriter /src/tests

getbash:
	docker run --rm -it --entrypoint "/bin/bash" -v `pwd`:/src/ -e KBC_DATADIR=/src/tests/data/ ${IMAGE}:latest

build:
	echo "Building ${IMAGE}:${VERSION}"
	docker build -t ${IMAGE}:${VERSION} -t ${IMAGE}:latest .

deploy:
	echo "Pusing to dockerhub"
	docker push ${IMAGE}:${VERSION}
	docker push ${IMAGE}:latest
