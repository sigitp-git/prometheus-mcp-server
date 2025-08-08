# Makefile for Amazon Managed Prometheus MCP Server

.PHONY: help install install-dev test test-cov lint format type-check clean run demo

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies with uv"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (ruff)"
	@echo "  format       - Format code (black + isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean up build artifacts"
	@echo "  run          - Run the MCP server"
	@echo "  demo         - Run comprehensive test demo"
	@echo "  check        - Run all quality checks"

# Installation
install:
	uv sync

install-dev:
	uv sync --extra dev --extra test

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=prometheus_mcp_server --cov-report=html --cov-report=term

test-simple:
	uv run python src/prometheus_mcp_server/simple_server.py

# Code quality
lint:
	uv run ruff check src/ tests/

format:
	uv run black src/ tests/
	uv run isort src/ tests/

format-check:
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

type-check:
	uv run mypy src/

# Combined quality check
check: format-check lint type-check test

# Running
run:
	uv run prometheus-mcp-server

demo:
	uv run python test_demo.py

# Maintenance
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build:
	uv build

# Development server with auto-reload
dev:
	uv run python -m prometheus_mcp_server.simple_server

# Update dependencies
update:
	uv sync --upgrade

# Lock dependencies
lock:
	uv lock

# Show dependency tree
deps:
	uv tree

# Python version management
python-install:
	uv python install 3.9 3.10 3.11 3.12

python-list:
	uv python list

# Virtual environment management
venv-create:
	uv venv

venv-remove:
	rm -rf .venv

# Add new dependencies
add-dep:
	@read -p "Enter package name: " pkg; uv add $$pkg

add-dev-dep:
	@read -p "Enter dev package name: " pkg; uv add --dev $$pkg
