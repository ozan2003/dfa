# Variables
UV := uv
SRC_DIR := src
TEST_DIR := tests

# Targets
.PHONY: install install-dev run test clean lint typecheck format check minver help
.SILENT: minver

# Install production dependencies
install:
	$(UV) sync --no-dev

# Install with development dependencies  
install-dev:
	$(UV) sync --extra dev

# Run the main program
run:
	$(UV) run python main.py

# Check minimum Python version requirements
minver:
	$(UV) run vermin --backport dataclasses --backport typing --no-parse-comments --eval-annotations .

# Run tests with pytest
test:
	$(UV) run pytest

# Run linting with ruff
lint:
	$(UV) run ruff check .

# Format code with ruff
format:
	$(UV) run ruff format .

# Run type checking with mypy
typecheck:
	$(UV) run mypy $(SRC_DIR)

# Run all checks (lint, format check, typecheck, test)
check: lint typecheck test
	@echo "All checks passed!"

# Clean up Python cache files and build artifacts
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

# Show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup targets:"
	@echo "   install      Install production dependencies"
	@echo "   install-dev  Install with development dependencies"
	@echo ""
	@echo "Development targets:"
	@echo "   run          Run the main program"
	@echo "   test         Run tests with pytest"
	@echo "   lint         Run linting with ruff"
	@echo "   format       Format code with ruff"
	@echo "   typecheck    Run type checking with mypy"
	@echo "   check        Run all checks (lint, typecheck, test)"
	@echo "   minver       Check minimum Python version requirements"
	@echo ""
	@echo "Utility targets:"
	@echo "   clean        Clean up cache files and build artifacts"
	@echo "   help         Show this help message"