"""
Pytest configuration for isolated test suite.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for absolute imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Pytest configuration
import pytest

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on directory."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Mark slow tests
        if "performance" in str(item.fspath) or "benchmark" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

# Fixtures for common test data
@pytest.fixture
def project_root_path():
    """Return the project root path."""
    return Path(__file__).parent.parent

@pytest.fixture
def engine_path():
    """Return the engine package path."""
    return Path(__file__).parent.parent / "engine"

@pytest.fixture
def data_path():
    """Return the data directory path."""
    return Path(__file__).parent.parent / "data"
