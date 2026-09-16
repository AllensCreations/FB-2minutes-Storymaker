.PHONY: setup install dev test lint format type-check run web sample-assets clean help

PYTHON ?= $(shell which python3 2>/dev/null || which python 2>/dev/null || echo python3)

# Setup & Installation
setup:
	@chmod +x setup_local.sh
	@./setup_local.sh

install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

# Running the Storymaker
run:
	$(PYTHON) main.py

web:
	$(PYTHON) main.py --web

sample-assets:
	$(PYTHON) scripts/generate_sample_assets.py

# Testing
test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

# Code Quality
lint:
	flake8 src/

format:
	black src/
	isort src/

type-check:
	mypy src/

# Cleanup
clean:
	rm -rf assets/processed/*
	rm -rf assets/output/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleaned generated assets and caches."

# Help
help:
	@echo "FB 2minutes Storymaker - Available Commands:"
	@echo "  make setup         - Run full local setup (FFmpeg check, venv, dependencies, assets)"
	@echo "  make run           - Run the full storytelling pipeline and render final_story.mp4"
	@echo "  make web           - Launch the local Web UI Studio on http://localhost:8000"
	@echo "  make sample-assets - Regenerate demo sample story assets"
	@echo "  make test          - Run unit and pipeline integration tests"
	@echo "  make clean         - Remove generated outputs, processed files, and python caches"
	@echo "  make format        - Format source code with black and isort"
	@echo "  make lint          - Lint code with flake8"