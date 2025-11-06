#!/bin/bash
# Run tests with coverage

# Default: run all tests in 'tests/' folder
TEST_PATH=${1:-tests/}

# Run pytest with coverage and show missing lines in terminal
pytest --cov=src --cov-report=term-missing "$TEST_PATH"
