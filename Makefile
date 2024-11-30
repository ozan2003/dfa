# Variables
PYTHON := python3
SRC_DIR := src

# Targets
.PHONY: run test clean minver

# Run the main program.
run:
	$(PYTHON) $(SRC_DIR)/main.py

minver:
	vermin --backport dataclasses --backport typing --no-parse-comments --eval-annotations .

# Run tests with unittest.
test:
	$(PYTHON) -m unittest -vv

# Clean up Python cache files.
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
