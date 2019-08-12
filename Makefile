test:
	pipenv run test

lint:
	pipenv run check

requirements: requirements.txt requirements-dev.txt

requirements-dev.txt: Pipfile.lock
	echo "-r requirements.txt" > requirements-dev.txt
	pipenv lock --dev --requirements >> requirements-dev.txt

requirements.txt: Pipfile.lock
	pipenv lock --requirements > requirements.txt

clean:
	-find . -type f -name '*.pyc' -delete
	-rm -rf build dist *.egg-info

docker:
	docker build -t wittman/csrgenerator.com .

.PHONY: clean test
