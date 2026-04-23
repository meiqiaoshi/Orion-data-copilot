# Dev shortcuts (use the same Python you use for the project, e.g. conda env `dev`).
.PHONY: help lint test test-fast install-dev api docker-build docker-run compose-up

help:
	@echo "Targets:  make lint | test | test-fast | install-dev | api | docker-build | docker-run | compose-up"

lint:
	python -m ruff check app tests main.py scripts

test:
	python -m pytest -q

test-fast:
	python -m pytest -q -m "not integration"

install-dev:
	pip install -e ".[dev,api]"

api:
	uvicorn app.api:app --reload --host 127.0.0.1 --port 8000

docker-build:
	docker build -t orion-data-copilot .

docker-run:
	docker run --rm -p 8000:8000 orion-data-copilot

compose-up:
	docker compose up --build
