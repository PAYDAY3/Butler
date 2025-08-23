#!/bin/bash
# This script starts the Butler application.
# It ensures that the script is run from its own directory
# to handle relative paths correctly.

echo "Starting Butler application..."

# Get the directory where the script is located and change to it
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Run the main application using the python module flag
python -m butler.main

echo "Application closed."
