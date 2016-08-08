requirements:
	pip install -r requirements.txt

check:
	flake8 --max-line-length=120 *.py

clean:
	-find . -type f -name '*.pyc' -delete
	-rm -rf build dist *.egg-info

test:
	nosetests

.PHONY: requirements check clean test
