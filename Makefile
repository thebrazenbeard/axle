PYTHON ?= python3

.PHONY: test run compile validate

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

compile:
	PYTHONPATH=src $(PYTHON) -m compileall -q src tests

run:
	PYTHONPATH=src $(PYTHON) -m axle.server --config config/axle.example.toml

validate:
	$(PYTHON) scripts/validate_repository.py
	node --check ui/app.js
