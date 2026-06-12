# DiagAutoClinicOS Testing Documentation

## Overview

This directory contains comprehensive testing documentation for DiagAutoClinicOS, including guides for running tests, writing new tests, and testing procedures specific to South African automotive diagnostics.

## Testing Structure

```
docs/testing/
├── README.md                    # This file
├── TESTING_GUIDE.md            # General testing procedures
├── TESTING_CHEATSHEET.md       # Quick reference for common tasks
├── running_tests.md            # How to execute test suites
├── writing_tests.md            # Guidelines for writing new tests
├── mock_mode_guide.md          # Using mock mode for testing
├── ci_cd_setup.md              # CI/CD pipeline configuration
└── testing/
    └── README.md               # Additional testing resources
```

## Quick Start

### Running All Tests
```bash
# From project root
pytest
```

### Running Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# AutoDiag tests only
pytest tests/AutoDiag/
```

### Running with Coverage
```bash
pytest --cov=AutoDiag --cov=shared --cov-report=html
```

## Test Categories

### Unit Tests
- Test individual functions and classes
- Located in `tests/*/unit/`
- Should run quickly (< 1 second each)

### Integration Tests
- Test component interactions
- Located in `tests/*/integration/`
- May require mock hardware

### Functional Tests
- Test end-to-end workflows
- Located in `tests/*/functional/`
- May require real hardware in some cases

### Performance Tests
- Benchmark critical operations
- Located in `tests/performance/`

### Security Tests
- Validate security features
- Located in `tests/security/`

## Mock Testing

DiagAutoClinicOS includes comprehensive mock testing capabilities:

- **Mock ECU Engine**: Simulates vehicle ECUs
- **Mock Adapters**: Simulate OBD-II adapters
- **Mock Vehicles**: Pre-defined vehicle configurations
- **Mock DTCs**: Simulated diagnostic trouble codes

See [mock_mode_guide.md](mock_mode_guide.md) for details.

## South African Testing

Special considerations for South African automotive testing:

- Environmental factors (heat, dust, electrical interference)
- Fuel quality variations
- Local vehicle models (VW Polo/Golf dominance)
- Regulatory compliance (POPIA, local standards)

See general testing procedures for South African conditions.

## CI/CD Integration

Automated testing is configured for:
- GitHub Actions
- Local development
- Pre-release validation

See [ci_cd_setup.md](ci_cd_setup.md) for pipeline configuration.

## Writing Tests

### Test File Organization
```
tests/
├── conftest.py              # Shared test fixtures
├── pytest.ini              # Pytest configuration
└── [module]/
    ├── __init__.py
    ├── unit/
    │   └── test_[feature].py
    ├── integration/
    │   └── test_[feature].py
    └── functional/
        └── test_[feature].py
```

### Test Naming Conventions
- Files: `test_[feature].py`
- Classes: `Test[Feature]`
- Methods: `test_[scenario]_[expected_result]`

### Example Test
```python
import pytest
from shared.vin_decoder import VINDecoder

class TestVINDecoder:
    def test_valid_vw_vin(self):
        decoder = VINDecoder()
        result = decoder.decode("WVWZZZ1KZCW123456")
        assert result['make'] == 'Volkswagen'
        assert result['model'] == 'Golf'
```

## Test Fixtures

Common test fixtures available:
- `mock_ecu`: Simulated ECU for testing
- `mock_adapter`: Mock OBD-II adapter
- `sample_vin`: Valid VIN for testing
- `test_vehicle`: Complete vehicle configuration

## Performance Testing

Key performance metrics to monitor:
- Connection time (< 30 seconds)
- DTC scan time (< 60 seconds)
- Memory usage (< 200 MB)
- CPU usage (idle < 5%)

## Security Testing

Security test categories:
- Authentication bypass attempts
- Input validation
- Secure data handling
- Session management
- Device communication security

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Include docstrings and comments
3. Add to appropriate test category
4. Update this documentation if needed
5. Ensure tests pass in CI/CD

## Troubleshooting

### Common Issues

**Tests failing due to missing dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Mock tests not working:**
- Ensure mock mode is enabled
- Check mock fixture configurations
- Verify test isolation

**Performance tests inconsistent:**
- Run on dedicated hardware
- Close background applications
- Use consistent test data

## Resources

- [Main Testing Guide](TESTING_GUIDE.md)
- [Testing Cheatsheet](TESTING_CHEATSHEET.md)
- [Writing Tests Guide](writing_tests.md)
- [Mock Mode Guide](mock_mode_guide.md)
- [CI/CD Setup](ci_cd_setup.md)

---

*For questions or issues with testing, see [COMMUNITY_DISCUSSIONS.md](../../COMMUNITY_DISCUSSIONS.md)*
