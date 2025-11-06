@echo off
REM Run pytest with coverage

SET TEST_PATH=%1
IF "%TEST_PATH%"=="" SET TEST_PATH=tests

pytest --cov=src --cov-report=term-missing %TEST_PATH%
pause