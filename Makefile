.PHONY: help format style black test lint check docs
.DEFAULT_GOAL = help

PYTHON = python
PIP = pip
SHELL = bash

help:
	@printf "Usage:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[1;34mmake %-10s\033[0m%s\n", $$1, $$2}'

format:
	@printf "Checking code style with black...\n"
	black --check compress_pickle tests
	@printf "\033[1;34mBlack passes!\033[0m\n\n"

style:
	@printf "Checking code style with pylint...\n"
	pylint compress_pickle
	@printf "\033[1;34mPylint passes!\033[0m\n\n"

black:  # Format code in-place using black.
	black compress_pickle/ tests/

test:  # Test code using pytest.
	pytest -v --cov=compress_pickle --doctest-modules tests/ compress_pickle/ --cov-report term --cov-report html

lint: format style  # Lint code using black and pylint.

check: lint test  # Both lint and test code. Runs `make lint` followed by `make test`.

docs:
	cd docs/ && $(MAKE) -f Makefile html
