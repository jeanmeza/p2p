
# Stop on error
$ErrorActionPreference = "Stop"

# Create venv if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
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

# Check if uv is available
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Installing dependencies using uv..."
    uv pip install -r requirements.txt 
} else {
    Write-Host "Installing dependencies using pip..."
    pip install -r requirements.txt
}