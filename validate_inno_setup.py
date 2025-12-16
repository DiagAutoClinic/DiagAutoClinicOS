#!/usr/bin/env python3
"""
AutoDiag Pro - Inno Setup Script Validator
==========================================

This script validates the Inno Setup script and checks for common issues
before building the installer.

Usage:
    python validate_inno_setup.py

Author: DACOS Team
Version: 1.0
"""

import os
import sys
import re
from pathlib import Path
import subprocess

class InnoSetupValidator:
    def __init__(self):
        self.script_path = Path("AutoDiag_Setup.iss")
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate(self):
        """Run all validation checks"""
        print("[INFO] AutoDiag Pro - Inno Setup Validator")
        print("=" * 50)
        
        # Basic file validation
        self.check_script_exists()
        self.check_script_syntax()
        self.check_file_references()
        self.check_required_files()
        self.check_directory_structure()
        self.check_encoding()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
    
    def check_script_exists(self):
        """Check if the Inno Setup script exists"""
        if not self.script_path.exists():
            self.errors.append(f"Inno Setup script not found: {self.script_path}")
        else:
            self.info.append(f"[OK] Inno Setup script found: {self.script_path}")
    
    def check_script_syntax(self):
        """Basic syntax validation for the script"""
        if not self.script_path.exists():
            return
            
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic syntax issues
            lines = content.split('\n')
            
            # Check for balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Check for required sections
            required_sections = ['[Setup]', '[Files]', '[Icons]', '[Languages]']
            for section in required_sections:
                if section not in content:
                    self.warnings.append(f"Missing recommended section: {section}")
                else:
                    self.info.append(f"[OK] Found section: {section}")
            
            # Check for common syntax errors
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith(';'):
                    # Check for unclosed quotes
                    quote_count = line.count('"')
                    if quote_count % 2 != 0:
                        self.errors.append(f"Line {i}: Unclosed quote in: {line[:50]}...")
                    
                    # Check for basic Pascal syntax
                    if '=' in line and not any(x in line for x in ['==', '>=', '<=']):
                        parts = line.split('=')
                        if len(parts) == 2 and not parts[1].strip():
                            self.warnings.append(f"Line {i}: Empty value after assignment")
            
        except Exception as e:
            self.errors.append(f"Error reading script: {e}")
    
    def check_file_references(self):
        """Check if referenced files exist"""
        if not self.script_path.exists():
            return
            
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract file references
            file_patterns = [
                r'Source:\s*"([^"]+)"',
                r'InfoBeforeFile\s*=\s*"([^"]+)"',
                r'LicenseFile\s*=\s*"([^"]+)"',
                r'SetupIconFile\s*=\s*"([^"]+)"'
            ]
            
            referenced_files = []
            for pattern in file_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                referenced_files.extend(matches)
            
            for file_ref in referenced_files:
                file_path = Path(file_ref)
                if file_path.exists():
                    self.info.append(f"[OK] Referenced file found: {file_ref}")
                else:
                    # Check if it's a directory pattern
                    if '*' in file_ref or '?' in file_ref:
                        parent_dir = file_path.parent
                        if parent_dir.exists():
                            self.info.append(f"[OK] Directory pattern found: {file_ref}")
                        else:
                            self.warnings.append(f"Directory pattern may not match: {file_ref}")
                    else:
                        self.warnings.append(f"Referenced file not found: {file_ref}")
        
        except Exception as e:
            self.errors.append(f"Error checking file references: {e}")
    
    def check_required_files(self):
        """Check if all required project files exist"""
        required_files = [
            "launcher.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        required_dirs = [
            "AutoDiag",
            "shared",
            "assets"
        ]
        
        for file_name in required_files:
            file_path = Path(file_name)
            if file_path.exists():
                self.info.append(f"[OK] Required file found: {file_name}")
            else:
                self.errors.append(f"Missing required file: {file_name}")
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                self.info.append(f"[OK] Required directory found: {dir_name}")
            else:
                self.errors.append(f"Missing required directory: {dir_name}")
    
    def check_directory_structure(self):
        """Check the project directory structure"""
        expected_structure = {
            "AutoDiag": ["main.py", "config", "core", "ui"],
            "shared": ["__init__.py", "themes"],
            "assets": [],  # Optional files
            "Files": ["AutoDiag_Launcher.bat", "Python_Installation_Guide.txt", "Troubleshooting_Guide.txt"]
        }
        
        for dir_name, expected_files in expected_structure.items():
            dir_path = Path(dir_name)
            if dir_path.exists():
                if expected_files:
                    for file_name in expected_files:
                        file_path = dir_path / file_name
                        if file_path.exists():
                            self.info.append(f"[OK] Found in {dir_name}: {file_name}")
                        else:
                            self.warnings.append(f"Missing in {dir_name}: {file_name}")
            else:
                if dir_name == "Files":  # Files directory is optional
                    self.info.append("[INFO] Optional Files directory not found")
                else:
                    self.warnings.append(f"Directory not found: {dir_name}")
    
    def check_encoding(self):
        """Check file encoding and special characters"""
        if not self.script_path.exists():
            return
            
        try:
            # Try to read with UTF-8
            with open(self.script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for potential encoding issues
            special_chars = ['°', '²', '³', 'µ', '±', '×', '÷']
            found_special = [char for char in special_chars if char in content]
            
            if found_special:
                self.info.append(f"[OK] Special characters found (UTF-8 compatible): {found_special}")
            
            # Check line endings
            if '\r\n' in content:
                self.info.append("[OK] Windows line endings (CRLF) detected")
            elif '\n' in content:
                self.warnings.append("Unix line endings (LF) detected - consider using CRLF for Windows")
            
        except UnicodeDecodeError as e:
            self.errors.append(f"Encoding error: {e}")
        except Exception as e:
            self.errors.append(f"Error checking encoding: {e}")
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 50)
        print("VALIDATION RESULTS")
        print("=" * 50)
        
        if self.errors:
            print(f"\n[ERROR] ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n[WARNING] WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.info:
            print(f"\n[INFO] INFORMATION ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")
        
        print("\n" + "=" * 50)
        
        if self.errors:
            print("[FAIL] VALIDATION FAILED - Please fix errors before building")
            return False
        elif self.warnings:
            print("[WARNING] VALIDATION PASSED WITH WARNINGS - Review warnings")
            return True
        else:
            print("[SUCCESS] VALIDATION PASSED - Ready to build installer")
            return True
    
    def check_inno_setup_installation(self):
        """Check if Inno Setup is properly installed"""
        try:
            # Try to run Inno Setup compiler
            result = subprocess.run(['iscc', '/HELP'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                self.info.append("[OK] Inno Setup compiler (iscc) found in PATH")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.warnings.append("Inno Setup compiler (iscc) not found in PATH")
        self.warnings.append("Install Inno Setup from: https://jrsoftware.org/isdl.php")
        return False
    
    def generate_build_script(self):
        """Generate a simple build script"""
        build_script = """@echo off
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
"""
        
        try:
            with open("build_installer.bat", "w", encoding="utf-8") as f:
                f.write(build_script)
            self.info.append("[OK] Build script generated: build_installer.bat")
        except Exception as e:
            self.errors.append(f"Failed to generate build script: {e}")

def main():
    """Main validation function"""
    validator = InnoSetupValidator()
    
    # Run validation
    success = validator.validate()
    
    # Additional checks
    validator.check_inno_setup_installation()
    validator.generate_build_script()
    
    # Re-print results to include additional checks
    validator.print_results()
    
    # Provide next steps
    print("\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    
    if success:
        print("1. Install Inno Setup if not already installed")
        print("2. Open Inno Setup Compiler")
        print("3. Load the AutoDiag_Setup.iss script")
        print("4. Click Build -> Compile")
        print("5. Find the installer in the Output directory")
        print("\nAlternatively, run: build_installer.bat")
    else:
        print("1. Fix the errors listed above")
        print("2. Re-run this validator")
        print("3. Once all errors are resolved, proceed with building")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())