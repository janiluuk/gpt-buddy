# Testing Guide for gpt-buddy

## Overview
This directory contains the test suite for the gpt-buddy voice assistant application.

## Setup

### Install Test Dependencies
```bash
# Activate your virtual environment
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/unit/test_helpers.py
```

### Run Specific Test Class
```bash
pytest tests/unit/test_helpers.py::TestPlayAudio
```

### Run Specific Test Function
```bash
pytest tests/unit/test_helpers.py::TestPlayAudio::test_play_audio_with_valid_file
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Unit Tests
```bash
pytest tests/unit/
```

### Run Only Integration Tests
```bash
pytest tests/integration/
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests (test individual functions)
│   ├── test_helpers.py
│   ├── test_gpt.py
│   ├── test_apprise_sender.py
│   └── test_scheduled_image.py
├── integration/             # Integration tests (test multiple components)
│   └── (future tests)
└── fixtures/                # Test data files
    └── (test audio, images, etc.)
```

## Writing New Tests

### Example Test Structure
```python
import pytest
from unittest.mock import Mock, patch

def test_example_function(mocker):
    """Test description"""
    # Arrange
    mock_dependency = mocker.patch('module.dependency')
    mock_dependency.return_value = "expected value"
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == "expected value"
    mock_dependency.assert_called_once()
```

### Using Fixtures
Fixtures are defined in `conftest.py` and can be used by adding them as function parameters:

```python
def test_with_fixture(mock_openai_client):
    # mock_openai_client is automatically provided
    result = some_function(mock_openai_client)
    assert result is not None
```

## Current Test Coverage

### Unit Tests Implemented
- ✅ helpers.py - Audio playback and image display
- ✅ gpt.py - OpenAI API interactions
- ✅ apprise_sender.py - Notification sending
- ✅ scheduled_image.py - Scheduled image generation

### Tests Still Needed
- ⏳ main.py - Main application loop (needs refactoring first)
- ⏳ Integration tests for full conversation flow
- ⏳ Edge case tests for error handling
- ⏳ Security tests for input validation

## Coverage Goals
- Overall: >80%
- helpers.py: >90% (security critical)
- gpt.py: >85%
- apprise_sender.py: >80%
- scheduled_image.py: >80%

## Continuous Integration
Tests should be run automatically on every commit via CI/CD pipeline.

### Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest tests/unit/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. You're in the project root directory
2. Your virtual environment is activated
3. Test dependencies are installed

### Mock Not Working
Ensure you're patching the right location. Patch where the object is used, not where it's defined:
```python
# If helpers.py does: from vlc import MediaPlayer
# Patch it as: mocker.patch('helpers.MediaPlayer')

# If helpers.py does: import vlc
# Patch it as: mocker.patch('vlc.MediaPlayer')
```

## Additional Resources
- [pytest documentation](https://docs.pytest.org/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
