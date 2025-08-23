@echo off
REM This script starts the Butler application.
REM It ensures that the script is run from its own directory
REM to handle relative paths correctly.

echo Starting Butler application...

REM Change directory to the script's location
cd /d "%~dp0"

REM Run the main application using the python module flag
python -m butler.main

echo Application closed.
pause
