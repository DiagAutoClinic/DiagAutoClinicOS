# 🚀 AutoDiag Testing Cheat Sheet

## ⚡ Quick Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=AutoDiag --cov=shared --cov-report=html

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests
pytest -m security          # Security tests
pytest -m "not slow"        # Skip slow tests

# Run tests in parallel
pytest -n auto

# Stop on first failure
pytest -x

# Show coverage report
open htmlcov/index.html     # macOS/Linux
start htmlcov/index.html    # Windows
```

---

## 📝 Writing Tests Template

```python
import pytest

class TestFeatureName:
    """Test suite for FeatureName"""
    
    def test_basic_functionality(self, mock_fixture):
        """Test basic feature works"""
        # Arrange
        expected = "result"
        
        # Act
        actual = function_to_test()
        
        # Assert
        assert actual == expected
    
    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_multiple_inputs(self, input, expected):
        """Test with multiple inputs"""
        assert function_to_test(input) == expected
```

---

## 🎯 Test Markers

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.security       # Security test
@pytest.mark.hardware       # Hardware test
@pytest.mark.slow           # Slow test (>1s)
@pytest.mark.skip          # Skip test
@pytest.mark.skipif        # Conditional skip
```

---

## 🔧 Common Fixtures

```python
# Available fixtures (see conftest.py)
def test_example(
    qapp,                          # Qt application
    mock_device_handler,           # Mock device
    mock_dtc_database,             # DTC database
    mock_security_manager,         # Security
    sample_dtc_codes,              # Sample DTCs
    sample_vin_codes,              # Sample VINs
):
    pass
```

---

## 🧪 Assertion Examples

```python
# Basic assertions
assert value == expected
assert value != unexpected
assert value is True
assert value is not None
assert value in collection
assert len(collection) > 0

# Exception testing
with pytest.raises(ValueError):
    function_that_raises()

# Approximate comparisons
assert value == pytest.approx(3.14, abs=0.01)

# String matching
assert "substring" in string
assert string.startswith("prefix")
assert string.endswith("suffix")
```

---

## 📊 Coverage Commands

```bash
# Generate HTML coverage
pytest --cov=AutoDiag --cov-report=html

# Show missing lines
pytest --cov=AutoDiag --cov-report=term-missing

# XML for CI
pytest --cov=AutoDiag --cov-report=xml

# Multiple directories
pytest --cov=AutoDiag --cov=shared --cov-report=html
```

---

## 🐛 Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Show local variables
pytest -l

# Verbose output
pytest -vv

# Show print statements
pytest -s

# Last failed tests only
pytest --lf

# Show slowest tests
pytest --durations=10
```

---

## 🔒 Security Testing

```python
def test_security_feature(mock_security_manager):
    """Test security without exposing secrets"""
    # Test INTERFACE, not IMPLEMENTATION
    result = mock_security_manager.authenticate_user('user', 'pass')
    assert isinstance(result, tuple)
    assert len(result) == 2
    # Never test actual algorithms!
```

---

## 🎪 Mock Examples

```python
from unittest.mock import Mock, MagicMock, patch

# Basic mock
mock_obj = Mock()
mock_obj.method.return_value = "mocked"

# Mock with side effects
mock_obj.method.side_effect = [1, 2, 3]

# Verify calls
mock_obj.method.assert_called_once()
mock_obj.method.assert_called_with(arg1, arg2)

# Patch
@patch('module.function')
def test_with_patch(mock_function):
    mock_function.return_value = "patched"
```

---

## 📈 Performance Testing

```python
def test_performance(benchmark, mock_database):
    """Benchmark function performance"""
    result = benchmark(mock_database.search_dtcs, 'P0')
    assert len(result) > 0

# Run benchmarks
pytest --benchmark-only
```

---

## 🌐 Platform-Specific

```bash
# Linux (with xvfb for Qt)
xvfb-run -a pytest tests/

# Windows
pytest tests/

# macOS
pytest tests/

# Skip platform-specific tests
pytest -m "not linux"
pytest -m "not windows"
```

---

## 📦 Test File Organization

```
tests/
├── conftest.py              # Shared fixtures
├── pytest.ini               # Configuration
├── unit/                    # Component tests
├── integration/             # System tests
├── security/                # Security tests
├── functional/              # E2E tests
└── performance/             # Performance tests
```

---

## ✅ Pre-Commit Checklist

Before pushing code:

```bash
# 1. Run tests
pytest

# 2. Check coverage
pytest --cov=AutoDiag --cov-report=term-missing

# 3. Format code
black AutoDiag/ shared/ tests/

# 4. Sort imports
isort AutoDiag/ shared/ tests/

# 5. Lint code
flake8 AutoDiag/ shared/ tests/

# 6. Type check
mypy AutoDiag/ shared/
```

---

## 🚨 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError` | `pip install -r requirements-dev.txt` |
| `Qt platform plugin` | `export QT_QPA_PLATFORM=offscreen` |
| `Permission denied /dev/tty` | `sudo usermod -a -G dialout $USER` |
| Tests hang | `pytest --timeout=60` |
| Import errors | Run from project root |

---

## 📞 Need Help?

```bash
# Show available fixtures
pytest --fixtures

# Show available markers
pytest --markers

# Help
pytest --help

# Version info
pytest --version
```

---

## 🎯 Coverage Goals

| Component | Target |
|-----------|--------|
| Device Handler | 90% |
| DTC Database | 95% |
| Security Module | 100% |
| UI Components | 70% |
| **Overall** | **85%** |

---

## 🔥 Power User Tips

```bash
# Run tests matching pattern
pytest -k "device or hardware"

# Parallel + coverage
pytest -n auto --cov=AutoDiag

# Watch mode (requires pytest-watch)
ptw -- --cov=AutoDiag

# Generate badge
coverage-badge -o coverage.svg -f

# Clear cache
pytest --cache-clear

# Collect tests only (don't run)
pytest --collect-only
```

---

## 📚 Quick Links

- [Full Testing Guide](./TESTING_GUIDE.md)
- [pytest docs](https://docs.pytest.org/)
- [Coverage docs](https://coverage.readthedocs.io/)
- [GitHub Actions](../.github/workflows/autodiag-tests.yml)

---

**Pro Tip:** Bookmark this page! 🔖

**Last Updated:** October 19, 2025
