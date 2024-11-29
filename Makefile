# Variables
PYTHON := python3
SRC_DIR := src
TEST_DIR := tests
PYTEST := $(PYTHON) -m unittest discover -s

# Targets
.PHONY: run test clean

# Run the main program.
run:
	$(PYTHON) $(SRC_DIR)/main.py

# Run tests with unittest.
test:
	$(PYTEST) $(TEST_DIR)

# Clean up Python cache files.
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
