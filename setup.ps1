
# Stop on error
$ErrorActionPreference = "Stop"

Write-Host "=== Erasure Coding Project Setup ==="

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Detected Python version: $pythonVersion"
} catch {
    Write-Error "Error: Python is not installed or not in PATH. Please install Python 3.13 or later and try again"
    exit 1
}

# Check if Python version meets minimum requirement (3.13+)
try {
    python -c "import sys; assert sys.version_info >= (3, 13), f'Python 3.13+ required, got {sys.version_info.major}.{sys.version_info.minor}'"
    Write-Host "Python version check passed"
} catch {
    Write-Error "Error: Python 3.13 or later is required. Please upgrade your Python installation and try again"
    exit 1
}

# Create venv if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    Write-Host "✓ Virtual environment created"
} else {
    Write-Host "✓ Virtual environment already exists"
}

# Activate the venv
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..."
    & $venvActivate
} else {
    Write-Error "Cannot find Activate.ps1 to activate the virtual environment."
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Check if uv is available
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Using uv to install dependencies..."
    uv pip install -r requirements.txt 
    Write-Host "✓ Dependencies installed with uv"
} else {
    Write-Host "uv not found, using pip to install dependencies..."
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed with pip"
}

Write-Host ""
Write-Host "=== Setup Complete! ==="
Write-Host "To activate the environment in the future, run:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To run a simulation example:"
Write-Host "  python queue_sim.py --lambd 0.95 --mu 1 --d 10 --n 10 --csv out.csv --max-t 1000000 --seed 42"