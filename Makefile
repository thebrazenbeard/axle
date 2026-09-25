PYTHON ?= python3

.PHONY: test run compile

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

compile:
	PYTHONPATH=src $(PYTHON) -m compileall -q src tests

run:
	PYTHONPATH=src $(PYTHON) -m axle.server --config config/axle.example.toml
