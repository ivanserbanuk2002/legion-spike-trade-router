PYTHON ?= python

.PHONY: lint test run

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m uvicorn app.main:app --reload
