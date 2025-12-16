@echo off
REM AutoDiag Pro - Build Script
echo Building AutoDiag Pro installer...

REM Check if Inno Setup is installed
iscc /HELP >nul 2>&1
if errorlevel 1 (
    echo Error: Inno Setup compiler not found
    echo Please install Inno Setup from https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

REM Compile the installer
echo Compiling installer...
iscc AutoDiag_Setup.iss

if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo Build completed successfully!
echo Check the Output directory for the installer
pause
