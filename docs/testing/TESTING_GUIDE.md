# 🧪 AutoDiag v2 Beta - Testing Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Test Structure](#test-structure)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Coverage Reports](#coverage-reports)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This testing framework provides **comprehensive, security-conscious testing** for AutoDiag v2 Beta without exposing sensitive algorithms or proprietary code.

### Test Coverage Goals

- ✅ **85%+ code coverage** (industry standard)
- ✅ **100% critical path coverage** (connection, DTC operations)
- ✅ **25+ brand protocols tested**
- ✅ **All hardware adapters verified**
- ✅ **Mock mode 100% functional**

### Testing Principles

1. **Security First**: Never expose proprietary algorithms
2. **Mock by Default**: Test without physical hardware
3. **Fast Execution**: Full suite < 5 minutes
4. **Clear Failures**: Descriptive error messages
5. **Maintainable**: Easy to add new tests

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to project root
cd DiagAutoClinicOS

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
pytest --version
```

### Run All Tests

```bash
# Run complete test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=AutoDiag --cov=shared --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Security tests only
pytest tests/ -m security

# Hardware tests (mock mode)
pytest tests/ -m hardware

# Skip slow tests
pytest tests/ -m "not slow"
```

---

## 📁 Test Structure

```
DiagAutoClinicOS/
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── pytest.ini                     # Configuration
│   │
│   ├── unit/                          # Component tests
│   │   ├── test_device_handler.py
│   │   ├── test_dtc_database.py
│   │   ├── test_vin_decoder.py
│   │   └── test_brand_database.py
│   │
│   ├── integration/                   # System tests
│   │   ├── test_diagnostic_workflow.py
│   │   ├── test_hardware_connection.py
│   │   └── test_dtc_operations.py
│   │
│   ├── security/                      # Security tests
│   │   ├── test_authentication.py
│   │   ├── test_authorization.py
│   │   └── test_audit_logging.py
│   │
│   ├── functional/                    # End-to-end tests
│   │   ├── test_full_diagnostic.py
│   │   └── test_special_functions.py
│   │
│   └── performance/                   # Performance tests
│       ├── test_dtc_search_speed.py
│       └── test_device_detection_speed.py
```

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Very verbose (show test names)
pytest -vv

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/unit/test_device_handler.py

# Run specific test function
pytest tests/unit/test_device_handler.py::test_device_handler_initialization

# Run tests matching pattern
pytest -k "device or hardware"
```

### Advanced Options

```bash
# Parallel execution (faster)
pytest -n auto

# Show slowest 10 tests
pytest --durations=10

# Generate HTML report
pytest --html=report.html --self-contained-html

# Generate JSON report
pytest --json-report --json-report-file=report.json

# Run with timeout (prevent hanging tests)
pytest --timeout=300

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

### Coverage Options

```bash
# Basic coverage
pytest --cov=AutoDiag

# Coverage with missing lines
pytest --cov=AutoDiag --cov-report=term-missing

# HTML coverage report
pytest --cov=AutoDiag --cov-report=html

# XML coverage (for CI)
pytest --cov=AutoDiag --cov-report=xml

# Coverage for multiple directories
pytest --cov=AutoDiag --cov=shared --cov-report=html
```

---

## ✍️ Writing Tests

### Test Structure

```python
import pytest

class TestYourFeature:
    """Test suite for your feature"""
    
    def test_basic_functionality(self):
        """Test basic feature works"""
        # Arrange
        expected = "result"
        
        # Act
        actual = your_function()
        
        # Assert
        assert actual == expected
    
    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            your_function_that_raises()
```

### Using Fixtures

```python
def test_with_fixture(mock_device_handler):
    """Test using a fixture"""
    # Fixture provides mock_device_handler
    assert mock_device_handler.mock_mode == True
```

### Parametrized Tests

```python
@pytest.mark.parametrize("code,expected", [
    ("P0300", "Misfire"),
    ("P0420", "Catalyst"),
    ("U0100", "Communication"),
])
def test_dtc_lookup(code, expected, mock_dtc_database):
    """Test DTC lookup for multiple codes"""
    info = mock_dtc_database.get_dtc_info(code)
    assert expected in info['description']
```

### Markers

```python
@pytest.mark.unit
def test_unit_level():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration_level():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test (>1 second)"""
    import time
    time.sleep(2)

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Skipped test"""
    pass
```

### Mocking

```python
from unittest.mock import Mock, MagicMock, patch

def test_with_mock():
    """Test with mock object"""
    mock_obj = Mock()
    mock_obj.method.return_value = "mocked"
    
    result = mock_obj.method()
    assert result == "mocked"

@patch('module.function')
def test_with_patch(mock_function):
    """Test with patched function"""
    mock_function.return_value = "patched"
    # Your test code here
```

---

## 📊 Coverage Reports

### Generating Reports

```bash
# Generate HTML report
pytest --cov=AutoDiag --cov=shared --cov-report=html

# Open HTML report
open htmlcov/index.html
```

### Understanding Coverage

- **Green lines**: Code is covered by tests
- **Red lines**: Code is NOT covered by tests
- **Orange lines**: Code is partially covered

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Device Handler | 90% | TBD |
| DTC Database | 95% | TBD |
| Security Module | 100% | TBD |
| UI Components | 70% | TBD |
| Overall | 85% | TBD |

---

## 🔄 CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Every push to `main`, `develop`, `feature/*`
- Every pull request
- Daily at 2 AM UTC
- Manual trigger via Actions tab

### Viewing CI Results

1. Go to **Actions** tab on GitHub
2. Click on latest workflow run
3. View job results and logs
4. Download artifacts (coverage reports, benchmarks)

### CI Test Matrix

| OS | Python Versions |
|----|-----------------|
| Ubuntu | 3.8, 3.9, 3.10, 3.11 |
| Windows | 3.8, 3.9, 3.10, 3.11 |
| macOS | 3.8, 3.9, 3.10, 3.11 |

---

## 🐛 Troubleshooting

### Common Issues

#### Qt Platform Plugin Error

```
qt.qpa.plugin: Could not find the Qt platform plugin
```

**Solution (Linux):**
```bash
sudo apt-get install libxcb-xinerama0 libdbus-1-3
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/
```

#### Import Errors

```
ModuleNotFoundError: No module named 'shared'
```

**Solution:**
```bash
# Ensure you're in project root
cd DiagAutoClinicOS

# Install in development mode
pip install -e .

# Or run with PYTHONPATH
PYTHONPATH=. pytest tests/
```

#### Serial Port Permission Denied

```
PermissionError: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**Solution (Linux):**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login, or use
newgrp dialout
```

#### Tests Hang or Timeout

**Solution:**
```bash
# Run with timeout
pytest --timeout=60

# Run without slow tests
pytest -m "not slow"

# Increase timeout in pytest.ini
# timeout = 600
```

#### Coverage Not Generated

**Solution:**
```bash
# Install coverage plugin
pip install pytest-cov

# Ensure correct paths
pytest --cov=AutoDiag --cov=shared

# Check .coveragerc file exists
```

### Debug Mode

```bash
# Run tests with debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb -x

# Show local variables on failure
pytest -l --tb=long

# Verbose logging
pytest --log-cli-level=DEBUG
```

### Performance Issues

```bash
# Run tests in parallel
pytest -n auto

# Profile test execution
pytest --durations=0

# Skip slow tests
pytest -m "not slow"
```

---

## 📝 Best Practices

### 1. Test Naming Convention

```python
# Good ✅
def test_device_connects_successfully():
def test_dtc_lookup_returns_valid_info():
def test_security_authentication_fails_with_invalid_password():

# Bad ❌
def test_1():
def test_stuff():
def test_it_works():
```

### 2. Arrange-Act-Assert Pattern

```python
def test_clear_dtcs():
    # Arrange: Set up test conditions
    handler = DeviceHandler(mock_mode=True)
    handler.connect_to_device("ELM327 USB", "AUTO")
    
    # Act: Perform the action
    result = handler.clear_dtcs()
    
    # Assert: Verify the outcome
    assert result == True
```

### 3. Single Responsibility

```python
# Good ✅ - Tests one thing
def test_device_connection():
    assert handler.connect_to_device("ELM327 USB", "AUTO")

def test_dtc_scanning():
    handler.connect_to_device("ELM327 USB", "AUTO")
    dtcs = handler.scan_dtcs()
    assert len(dtcs) > 0

# Bad ❌ - Tests multiple things
def test_everything():
    assert handler.connect_to_device("ELM327 USB", "AUTO")
    dtcs = handler.scan_dtcs()
    assert len(dtcs) > 0
    handler.clear_dtcs()
    live_data = handler.get_live_data('rpm')
    assert live_data > 0
```

### 4. Use Fixtures for Setup

```python
# Good ✅
@pytest.fixture
def connected_device():
    handler = DeviceHandler(mock_mode=True)
    handler.connect_to_device("ELM327 USB", "AUTO")
    yield handler
    handler.disconnect()

def test_with_connected_device(connected_device):
    dtcs = connected_device.scan_dtcs()
    assert len(dtcs) > 0

# Bad ❌
def test_without_fixture():
    handler = DeviceHandler(mock_mode=True)
    handler.connect_to_device("ELM327 USB", "AUTO")
    dtcs = handler.scan_dtcs()
    assert len(dtcs) > 0
    handler.disconnect()
```

### 5. Meaningful Assertions

```python
# Good ✅
def test_dtc_info():
    info = db.get_dtc_info('P0300')
    assert info['description'] == 'Random/Multiple Cylinder Misfire Detected'
    assert info['severity'] == 'High'
    assert info['category'] == 'Powertrain'

# Bad ❌
def test_dtc_info():
    info = db.get_dtc_info('P0300')
    assert info  # Too vague!
```

---

## 🎯 Test Checklist

Before committing code, ensure:

- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Code coverage ≥ 85%
- [ ] No security tests are skipped
- [ ] Tests run in < 5 minutes
- [ ] Mock mode works correctly
- [ ] No hardcoded passwords/secrets
- [ ] Tests are independent (no order dependency)
- [ ] Documentation is updated

---

## 📊 Test Metrics Dashboard

### Current Status (Update Weekly)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Total Tests | 100+ | TBD | 🟡 |
| Code Coverage | 85% | TBD | 🟡 |
| Test Duration | < 5min | TBD | 🟡 |
| Pass Rate | 100% | TBD | 🟡 |
| Critical Path Coverage | 100% | TBD | 🟡 |
| Security Tests | 20+ | TBD | 🟡 |

Legend: 🟢 Good | 🟡 In Progress | 🔴 Needs Attention

---

## 🚀 Advanced Topics

### Testing with Real Hardware

```python
@pytest.mark.hardware
@pytest.mark.skipif(not hardware_available(), reason="No hardware connected")
def test_real_elm327_connection():
    """Test with actual ELM327 device"""
    handler = DeviceHandler(mock_mode=False)
    # Real hardware test code...
```

### Performance Benchmarking

```python
def test_dtc_search_performance(benchmark, mock_dtc_database):
    """Benchmark DTC search speed"""
    result = benchmark(mock_dtc_database.search_dtcs, 'P0')
    assert len(result) > 0
```

### Snapshot Testing

```python
def test_ui_snapshot(snapshot):
    """Test UI hasn't changed unexpectedly"""
    widget = create_diagnostic_widget()
    snapshot.assert_match(widget.screenshot())
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=17, max_size=17))
def test_vin_validation_property(vin):
    """Test VIN validation with random inputs"""
    result = vin_decoder.is_valid(vin)
    assert isinstance(result, bool)
```

---

## 📚 Additional Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [PyQt6 testing guide](https://doc.qt.io/qtforpython-6/tutorials/index.html)
- [Coverage.py docs](https://coverage.readthedocs.io/)

### Videos
- [pytest Tutorial](https://www.youtube.com/watch?v=bbp_849-RZ4)
- [Test-Driven Development](https://www.youtube.com/watch?v=B1j6k2j2eJg)

### Books
- "Test-Driven Development with Python" by Harry Percival
- "Python Testing with pytest" by Brian Okken

---

## 🤝 Contributing Tests

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `test_<feature>.py`
3. Use descriptive test names
4. Add appropriate markers
5. Update this guide if needed

### Test Review Checklist

When reviewing test PRs:

- [ ] Tests are clear and readable
- [ ] Tests follow AAA pattern
- [ ] Appropriate fixtures are used
- [ ] Edge cases are covered
- [ ] Security considerations respected
- [ ] Documentation updated
- [ ] CI passes

---

## 🔒 Security Testing Guidelines

### What to Test

✅ **DO TEST:**
- Authentication flow (abstracted)
- Authorization checks
- Session management
- Audit logging
- Input validation
- Error messages (no info leakage)

❌ **DON'T TEST:**
- Actual encryption algorithms
- Key generation methods
- Specific IMMO calculations
- Proprietary protocols
- Security bypass techniques

### Example Security Test

```python
def test_authentication_flow(mock_security_manager):
    """Test authentication without exposing actual algorithm"""
    # Test the INTERFACE, not the IMPLEMENTATION
    success, message = mock_security_manager.authenticate_user('user', 'pass')
    assert isinstance(success, bool)
    assert isinstance(message, str)
```

---

## 📞 Support

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions, share ideas
- **Documentation**: Check docs/ directory
- **Email**: support@diagautoclinic.co.za

### Reporting Test Failures

When reporting test failures, include:

1. Full test output (`pytest -vv`)
2. Python version (`python --version`)
3. OS and version
4. pytest version (`pytest --version`)
5. Steps to reproduce
6. Expected vs actual behavior

---

## 🎉 Success Criteria

AutoDiag v2 is ready for release when:

✅ All tests pass on all platforms  
✅ Code coverage ≥ 85%  
✅ No critical security issues  
✅ Performance benchmarks met  
✅ Documentation complete  
✅ CI/CD pipeline green  
✅ Beta testers approve  

---

**Last Updated:** October 19, 2025  
**Version:** 2.0.0-beta  
**Maintainer:** DiagAutoClinic Team
