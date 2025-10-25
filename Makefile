.PHONY: help dev test lint format clean install

help:  ## Show this help message
	@echo "URL Shortener - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install:  ## Install dependencies
	python3 -m pip install -r requirements.txt

dev:  ## Start development server with auto-reload
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run test suite
	python3 -m pytest tests/ -v

test-cov:  ## Run tests with coverage report
	python3 -m pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:  ## Lint code with ruff
	ruff check app/ tests/

format:  ## Format code with ruff
	ruff format app/ tests/

clean:  ## Clean cache and database files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.db" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "Cleaned cache and database files"

check:  ## Run checks (lint + test)
	@echo "Running linter..."
	@make lint
	@echo ""
	@echo "Running tests..."
	@make test
