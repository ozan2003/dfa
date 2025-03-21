# Variables
PYTHON := python3
SRC_DIR := src

# Targets
.PHONY: run test clean minver help
.SILENT: minver # Don't show the command being run.

# Run the main program.
run:
	$(PYTHON) $(SRC_DIR)/main.py

minver:
	# Check for vermin.
	vermin --version > /dev/null || (echo "vermin is not installed. Run 'pip install vermin' to install it." && exit 1)

	vermin --backport dataclasses --backport typing --no-parse-comments --eval-annotations .

# Run tests with pytest.
test:
	$(PYTHON) -m pytest -v

# Clean up Python cache files.
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -r .pytest_cache

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "   run      Run the main program."
	@echo "   test     Run tests with pytest."
	@echo "   clean    Clean up Python cache files."
	@echo "   minver   Check the minimum Python version required. (requires vermin)"
	@echo "   help     Show this help message."