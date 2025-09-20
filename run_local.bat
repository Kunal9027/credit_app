@echo off
echo Credit Approval System - Local Development Setup
echo =============================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.11+ and try again.
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if Redis is running
echo Checking Redis connection...
python -c "import socket; s=socket.socket(); result=s.connect_ex(('localhost', 6379)); s.close(); exit(1 if result != 0 else 0)" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Redis is not running or not accessible at localhost:6379
    echo For Celery to work properly, you need Redis running.
    echo.
    echo For Windows, download Redis from https://github.com/microsoftarchive/redis/releases
    echo - Download the MSI installer (Redis-x64-3.0.504.msi is recommended)
    echo - Run the installer and follow the instructions
    echo.
    echo Alternatively, you can run just the Redis service from Docker:
    echo docker run -d -p 6379:6379 redis:7
    echo.
    echo Press any key to continue anyway or Ctrl+C to exit...
    pause >nul
)

REM Run setup script
echo Running setup script...
python setup_local.py

REM Start development server
echo Starting development server...
python credit_project\manage.py runserver

pause