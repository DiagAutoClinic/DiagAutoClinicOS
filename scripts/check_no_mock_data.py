#!/usr/bin/env python3
"""
Build Check Script: Ensure No Mock Data in Production Code
Fails the build if any mock, simulation, or fake data is found in Python files.
"""

import os
import sys
import re
from pathlib import Path

# Patterns that indicate mock/simulation data
MOCK_PATTERNS = [
    r'\bmock\b',
    r'\bMock\b',
    r'\bsimulation\b',
    r'\bsimulate\b',
    r'\bfake\b',
    r'\bfallback\b',
    r'\bdummy\b',
    r'\btest.*data\b',
    r'\bfake.*data\b',
    r'\bmock.*data\b',
    r'\bsample.*data\b',
    r'\bdemo.*data\b',
    r'\bexample.*data\b',
    r'\brandom\.',
    r'\brandom\b.*\(.*\)',
]

# Files and directories to exclude from check
EXCLUDE_PATHS = [
    'tests/',
    'test_',
    'scripts/',
    '__pycache__/',
    '.git/',
    '.venv/',
    'venv/',
    'node_modules/',
    'build/',
    'dist/',
    'check_no_mock_data.py',
    'conftest.py',
    'examine_db_schema.py',  # Database utility script
    'ai/',  # AI modules may have test data
    'api_tests/',
    'shared/',
    'AutoECU/',
    'AutoKey/',
    'can_bus_data_backup/',
    'dacos.co.za/',
    'website/',
]

# Specific allowed mock usage in test files
ALLOWED_MOCK_IN_TESTS = [
    'tests/',
    'conftest.py',
]

def should_exclude_file(filepath: str) -> bool:
    """Check if file should be excluded from mock data check"""
    # Normalize path separators
    filepath = filepath.replace('\\', '/')
    for exclude in EXCLUDE_PATHS:
        if exclude.rstrip('/') in filepath:
            return True
    return False

def is_test_file(filepath: str) -> bool:
    """Check if file is a test file where some mock usage might be allowed"""
    for allowed in ALLOWED_MOCK_IN_TESTS:
        if allowed in filepath:
            return True
    return False

def check_file_for_mock_data(filepath: str) -> list:
    """Check a single file for mock data patterns"""
    violations = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith('#') or '"""' in stripped or "'''" in stripped:
                continue

            for pattern in MOCK_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Allow some mock usage in test files
                    if is_test_file(filepath):
                        # Allow specific test-related mock usage
                        if any(term in line.lower() for term in ['pytest.fixture', 'mock_', '@mock', 'unittest.mock']):
                            continue

                    violations.append({
                        'file': filepath,
                        'line': line_num,
                        'pattern': pattern,
                        'content': line.strip()
                    })

    except Exception as e:
        print(f"Error checking file {filepath}: {e}")

    return violations

def main():
    """Main check function"""
    print("Checking for mock data in production code...")

    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if not should_exclude_file(filepath):
                    python_files.append(filepath)

    print(f"Checking {len(python_files)} Python files...")

    all_violations = []
    for filepath in python_files:
        violations = check_file_for_mock_data(filepath)
        all_violations.extend(violations)

    if all_violations:
        print(f"\nFOUND {len(all_violations)} MOCK DATA VIOLATIONS!")
        print("=" * 60)

        for violation in all_violations:
            print(f"VIOLATION: {violation['file']}:{violation['line']}")
            print(f"   Pattern: {violation['pattern']}")
            try:
                print(f"   Content: {violation['content']}")
            except UnicodeEncodeError:
                print(f"   Content: {violation['content'].encode('ascii', 'replace').decode('ascii')}")
            print()

        print("=" * 60)
        print("BUILD FAILED: Mock data found in production code!")
        print("Remove all mock, simulation, and fake data before proceeding.")
        sys.exit(1)
    else:
        print("No mock data found in production code!")
        print("Build check passed.")
        sys.exit(0)

if __name__ == '__main__':
    main()