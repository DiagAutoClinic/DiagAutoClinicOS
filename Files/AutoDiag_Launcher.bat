@echo off
REM AutoDiag Pro Launcher Batch File
REM This file is created by the installer to launch AutoDiag Pro

echo Starting AutoDiag Pro...
echo.

REM Change to the application directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Launch the launcher script
python launcher.py

REM If launcher fails, show error
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start AutoDiag Pro.
    echo Check launcher_debug.log for details.
    echo.
    pause
)

exit /b 0