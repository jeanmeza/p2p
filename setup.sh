#!/bin/bash

if [ ! -d ".venv" ]; then
  echo "Creating environment"
  python3 -m venv .venv
fi

echo "Activating environment"
source .venv/bin/activate

# Use uv if available, otherwise fallback to pip
if command -v uv &>/dev/null; then
  echo "Using uv to install dependencies..."
  uv pip install -r requirements.txt
else
  echo "Using pip to install dependencies..."
  pip install -r requirements.txt
fi
