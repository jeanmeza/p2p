
#!/bin/bash

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Activate it
source .venv/bin/activate

# Use uv if available, otherwise fallback to pip
if command -v uv &> /dev/null
then
  echo "Using uv to install dependencies..."
  uv pip install -r requirements.txt
else
  echo "Using pip to install dependencies..."
  pip install -r requirements.txt
fi