# AutoDiag Pro - Build Script (PowerShell)
Write-Host "Building AutoDiag Pro installer..." -ForegroundColor Green

# Check if Inno Setup is installed
$isccPath = "C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if (!(Test-Path $isccPath)) {
    Write-Host "Error: Inno Setup compiler not found at $isccPath" -ForegroundColor Red
    Write-Host "Please install Inno Setup from https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Compile the installer
Write-Host "Compiling installer..." -ForegroundColor Cyan
& $isccPath AutoDiag_Setup.iss

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Check the Output directory for the installer" -ForegroundColor Green
} else {
    Write-Host "Error: Build failed" -ForegroundColor Red
}

Read-Host "Press Enter to exit"