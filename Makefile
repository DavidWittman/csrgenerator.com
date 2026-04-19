test:
	uv run pytest tests.py

lint:
	uv run flake8 --max-line-length=120 --exclude=.venv

requirements: requirements.txt requirements-dev.txt

requirements-dev.txt: uv.lock
	uv export --group dev -o requirements-dev.txt

requirements.txt: uv.lock
	uv export --no-dev -o requirements.txt

clean:
	-find . -type f -name '*.pyc' -delete
	-rm -rf build dist *.egg-info

docker:
	docker build --platform linux/amd64 -t wittman/csrgenerator.com .

.PHONY: clean test
