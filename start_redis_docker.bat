@echo off
echo Starting Redis using Docker...
echo ==============================

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed or not in PATH. Please install Docker and try again.
    exit /b 1
)

REM Check if Redis container is already running
docker ps --filter "name=credit_app_redis" --format "{{.Names}}" | findstr /i "credit_app_redis" >nul
if %ERRORLEVEL% equ 0 (
    echo Redis container is already running.
    goto :end
)

REM Check if Redis container exists but is stopped
docker ps -a --filter "name=credit_app_redis" --format "{{.Names}}" | findstr /i "credit_app_redis" >nul
if %ERRORLEVEL% equ 0 (
    echo Starting existing Redis container...
    docker start credit_app_redis
    goto :end
)

REM Start a new Redis container
echo Creating and starting new Redis container...
docker run -d --name credit_app_redis -p 6379:6379 redis:7

:end
echo.
echo Redis should now be available at localhost:6379
echo You can now run the application with run_local.bat
echo.
pause