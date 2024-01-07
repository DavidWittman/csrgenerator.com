test:
	pipenv run test

lint:
	pipenv run check

requirements: requirements.txt requirements-dev.txt

requirements-dev.txt: Pipfile.lock
	pipenv requirements --dev > requirements-dev.txt

requirements.txt: Pipfile.lock
	pipenv requirements > requirements.txt

clean:
	-find . -type f -name '*.pyc' -delete
	-rm -rf build dist *.egg-info

docker:
	docker build --platform linux/amd64 -t wittman/csrgenerator.com .

.PHONY: clean test
