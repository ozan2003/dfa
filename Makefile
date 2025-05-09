# Variables
PYTHON := python3
SRC_DIR := src
VENV := .venv
UV := uv
VENV_PYTHON := .venv/bin/python
VENV_ACTIVATE := . .venv/bin/activate

# Targets
.PHONY: run test clean help lint typecheck setup dev-setup
.SILENT: minver # Don't show the command being run.

# Run the main program.
run:
	$(VENV_PYTHON) $(SRC_DIR)/main.py

minver:
	# Check for vermin.
	$(VENV_ACTIVATE) && vermin --version > /dev/null || (echo "vermin is not installed. Run '$(UV) pip install vermin' to install it." && exit 1)

	$(VENV_ACTIVATE) && vermin --backport dataclasses --backport typing --no-parse-comments --eval-annotations .

# Run tests with pytest.
test:
	$(VENV_PYTHON) -m pytest -v

# Clean up Python cache files.
clean:
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .pytest_cache

# Setup the project for development
setup:
	$(UV) venv
	$(UV) pip install -e .

# Setup with development dependencies
dev-setup:
	$(UV) venv
	$(UV) pip install -e ".[dev]"

# Run linting with ruff
lint:
	$(VENV_PYTHON) -m ruff check .

# Run type checking with mypy
typecheck:
	$(VENV_PYTHON) -m mypy $(SRC_DIR)

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "   run          Run the main program."
	@echo "   test         Run tests with pytest."
	@echo "   clean        Clean up Python cache files."
	@echo "   minver       Check the minimum Python version required. (requires vermin)"
	@echo "   setup        Setup the project for development"
	@echo "   dev-setup    Setup with development dependencies"
	@echo "   lint         Run linting with ruff"
	@echo "   typecheck    Run type checking with mypy"
	@echo "   help         Show this help message."