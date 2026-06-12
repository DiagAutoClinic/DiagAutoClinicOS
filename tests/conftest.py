# tests/conftest.py
"""
pytest configuration – register custom markers used in the test suite.
"""
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: fast unit tests that do not require hardware or a display")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "mock: tests using mock hardware")
    config.addinivalue_line("markers", "hardware: tests that interact with real hardware")
    config.addinivalue_line("markers", "benchmark: performance benchmark tests")
