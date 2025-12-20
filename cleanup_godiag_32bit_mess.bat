@echo off
echo Cleaning up manual Godiag GD101 32-bit registry entry and local DLL...
echo.

:: Delete the manual registry entry (safe even if it doesn't exist)
reg delete "HKLM\SOFTWARE\WOW6432Node\PassThruSupport.04.04\GODIAG GD101" /f >nul 2>&1
if %errorlevel% == 0 (
    echo Registry entry deleted successfully.
) else (
    echo No registry entry found (already clean or never existed).
)
echo.

:: Delete the local copied DLL (uses quoted path to handle spaces/hyphens)
set "DLL_PATH=drivers\GODIAG_J2534_Driver\GODIAG_PT32.dll"
if exist "%DLL_PATH%" (
    del "%DLL_PATH%" /f /q
    echo Local GODIAG_PT32.dll deleted.
) else (
    echo Local DLL not found (already deleted or not present).
)
echo.

echo Cleanup complete! You're now on a clean slate.
echo Safe to install the official driver and switch to 64-bit Python.
pause