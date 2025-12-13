@echo off
REM AutoDiag Pro - Build Script
echo Building AutoDiag Pro installer...

REM Check if Inno Setup is installed
if not exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" (
    echo Error: Inno Setup compiler not found at expected location
    echo Please install Inno Setup from https://jrsoftware.org/isdl.php
    echo Expected location: C:\Program Files (x86)\Inno Setup 6\
    pause
    exit /b 1
)

REM Compile the installer
echo Compiling installer...
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" AutoDiag_Setup.iss

if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo Build completed successfully!
echo Check the Output directory for the installer
pause
