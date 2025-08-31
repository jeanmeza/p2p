#!/bin/bash

# Exit on any error
set -e

echo "=== Erasure Coding Project Setup ==="

# Check if Python 3 is available
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    echo "Please install Python 3.13 or later and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Detected Python version: $python_version"

# Check if Python version meets minimum requirement (3.13+)
if ! python3 -c "import sys; assert sys.version_info >= (3, 13)" 2>/dev/null; then
    echo "Error: Python 3.13 or later is required (detected: $python_version)"
    echo "Please upgrade your Python installation and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  echo "✓ Virtual environment created"
else
  echo "✓ Virtual environment already exists"
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip to latest version
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Use uv if available, otherwise fallback to pip
if command -v uv &>/dev/null; then
  echo "Using uv to install dependencies..."
  uv pip install -r requirements.txt
  echo "✓ Dependencies installed with uv"
else
  echo "uv not found, using pip to install dependencies..."
  pip install -r requirements.txt
  echo "✓ Dependencies installed with pip"
fi

echo ""
echo "=== Setup Complete! ==="
echo "To activate the environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run a simulation example:"
echo "  chmod u+x run_experiment_and_plot.sh && ./run_experiment_and_plot.sh"
