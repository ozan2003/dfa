# Variables
PYTHON := python3
SRC_DIR := src

# Targets
.PHONY: run test clean

# Run the main program.
run:
	$(PYTHON) $(SRC_DIR)/main.py

# Run tests with unittest.
test:
	$(PYTHON) -m unittest -v

# Clean up Python cache files.
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
