# Dev shortcuts (use the same Python you use for the project, e.g. conda env `dev`).
.PHONY: help lint test install-dev api

help:
	@echo "Targets:  make lint | test | install-dev | api"

lint:
	python -m ruff check app tests main.py scripts

test:
	python -m pytest -q

install-dev:
	pip install -e ".[dev,api]"

api:
	uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
