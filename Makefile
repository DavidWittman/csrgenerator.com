test:
	pipenv run test

lint:
	pipenv run check

requirements.txt: Pipfile.lock
	pipenv lock --requirements > requirements.txt

clean:
	-find . -type f -name '*.pyc' -delete
	-rm -rf build dist *.egg-info

docker:
	docker build -t wittman/csrgenerator.com .

.PHONY: clean test
