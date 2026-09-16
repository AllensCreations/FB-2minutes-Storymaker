.PHONY: install dev test lint format type-check run help

# Installation
install:
	pip install -e .

dev:
	pip install -e .[dev]

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

# Code quality
lint:
	flake8 src/

format:
	black src/
	isort src/

# Type checking
type-check:
	mypy src/
	pyright src/

# Running
run:
	python main.py

# Help
help:
	@echo "Available commands:"
	@echo "  make install     - Install package in development mode"
	@echo "  make dev         - Install with development dependencies"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make lint        - Run flake8 linting"
	@echo "  make format      - Format code with black and isort"
	@echo "  make type-check  - Run type checking with mypy and pyright"
	@echo "  make run         - Run the application"
	@echo "  make help        - Show this help"
