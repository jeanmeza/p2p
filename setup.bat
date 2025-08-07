@echo off

:: Check if .venv exists
if not exist ".venv" (
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Check if uv is available
where uv >nul 2>nul
if %errorlevel%==0 (
    echo Using uv to install dependencies...
    uv pip install -r requirements.txt 
) else (
    echo Using pip to install dependencies...
    pip install -r requirements.txt
)