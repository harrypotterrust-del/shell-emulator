PYTHON ?= python3
export PYTHONPATH := src

.PHONY: run test lint check

run:
	$(PYTHON) -m emulator $(ARGS)

test:
	$(PYTHON) -m pytest -q tests

lint:
	$(PYTHON) -m flake8 src tests

check: lint test
