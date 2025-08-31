@echo off

echo === Erasure Coding Project Setup ===

:: Check if Python is available
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.13 or later and try again
    exit /b 1
)

:: Check Python version meets minimum requirement (3.13+)
python -c "import sys; assert sys.version_info >= (3, 13), f'Python 3.13+ required, got {sys.version_info.major}.{sys.version_info.minor}'" >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python 3.13 or later is required
    python -c "import sys; print(f'Detected Python version: {sys.version_info.major}.{sys.version_info.minor}')"
    echo Please upgrade your Python installation and try again
    exit /b 1
)

echo Python version check passed

:: Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Check if uv is available
where uv >nul 2>nul
if %errorlevel%==0 (
    echo Using uv to install dependencies...
    uv pip install -r requirements.txt 
    echo ✓ Dependencies installed with uv
) else (
    echo uv not found, using pip to install dependencies...
    pip install -r requirements.txt
    echo ✓ Dependencies installed with pip
)

echo.
echo === Setup Complete! ===
echo To activate the environment in the future, run:
echo   .venv\Scripts\activate.bat
echo.
echo To run a simulation example:
echo   python queue_sim.py --lambd 0.95 --mu 1 --d 10 --n 10 --csv out.csv --max-t 1000000 --seed 42