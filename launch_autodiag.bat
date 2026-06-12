@echo off
echo Starting AutoDiag Diagnostic Suite v0.0.1...
echo.
echo ========================================
echo DiagAutoClinicOS - AutoDiag
echo Alpha Release - For Testing Only
echo ========================================
echo.

if exist "dist\AutoDiag.exe" (
    echo Found: dist\AutoDiag.exe
    echo.
    start "" "dist\AutoDiag.exe"
) else (
    echo ERROR: AutoDiag.exe not found in dist folder!
    echo.
    echo Please run: python build_installer.py
)

echo.
pause
