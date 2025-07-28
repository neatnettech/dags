# Test Suite Documentation

This directory contains comprehensive tests for the DAG Execution API, organized by test type and purpose.

## Test Structure

```
tests/
├── README.md                   # This file
├── conftest.py                 # Pytest configuration and shared fixtures
├── api/                        # API endpoint tests
│   ├── test_health_endpoints.py
│   └── test_manifest_endpoints.py
├── unit/                       # Unit tests
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_middleware.py
│   └── test_models.py
├── integration/                # Integration tests
│   └── test_manifest_execution.py
└── fixtures/                   # Test data
    └── data/
        └── new/
            ├── thomson1.thomson
            ├── thomson2.thomson
            ├── reuters1.reuters
            └── reuters2.reuters
```

## Running Tests

### Using the test runner script:

```bash
# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py unit        # Unit tests only
python run_tests.py api         # API tests only
python run_tests.py integration # Integration tests only
python run_tests.py fast        # All tests except slow ones

# With options
python run_tests.py all -v      # Verbose output
python run_tests.py unit --no-cov  # Without coverage
```

### Using pytest directly:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=dag_engine --cov-report=html

# Run specific test file
pytest tests/api/test_health_endpoints.py

# Run specific test class or method
pytest tests/api/test_health_endpoints.py::TestHealthEndpoints
pytest tests/api/test_health_endpoints.py::TestHealthEndpoints::test_root_endpoint

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m "not slow"    # Exclude slow tests
```

## Test Categories

### API Tests (`tests/api/`)
- **Purpose**: Test API endpoints, request/response formats, status codes
- **Coverage**: All API endpoints and their various response scenarios
- **Key Tests**:
  - Health and utility endpoints
  - Manifest execution endpoint
  - Error responses
  - Request validation

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: Models, exceptions, middleware, configuration
- **Key Tests**:
  - Pydantic model validation
  - Exception handling
  - Middleware functionality
  - Configuration loading

### Integration Tests (`tests/integration/`)
- **Purpose**: Test full workflow with real components
- **Coverage**: End-to-end manifest execution
- **Key Tests**:
  - Complete manifest execution flow
  - Dependency resolution
  - Concurrent execution
  - Performance metrics

## Key Test Fixtures

### `client`
- FastAPI test client for making API requests
- Automatically handles app lifecycle

### `sample_manifest`
- Valid manifest with two steps and dependencies
- Used for successful execution tests

### `manifest_with_cyclic_dependency`
- Manifest with circular dependencies
- Used for error handling tests

### `manifest_with_invalid_type`
- Manifest with unsupported interface type
- Used for validation tests

### `empty_manifest`
- Manifest with no steps
- Used for edge case testing

## Test Coverage

The test suite aims for >80% code coverage:

- **API Layer**: ~95% coverage
- **Models**: ~100% coverage
- **Exceptions**: ~90% coverage
- **Middleware**: ~85% coverage
- **Core Logic**: ~80% coverage

View coverage report:
```bash
pytest --cov-report=html
open htmlcov/index.html
```

## Writing New Tests

### 1. Choose the Right Category
- API tests for endpoint behavior
- Unit tests for isolated components
- Integration tests for workflows

### 2. Use Appropriate Fixtures
```python
def test_endpoint(client, sample_manifest):
    response = client.post("/api/v1/execute-manifest", 
                          json=sample_manifest.dict())
    assert response.status_code == 200
```

### 3. Follow Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### 4. Use Descriptive Names
```python
def test_manifest_execution_with_invalid_prerequisites():
    """Test that manifest execution fails gracefully with invalid prerequisites"""
    pass
```

### 5. Test Both Success and Failure Cases
```python
def test_health_check_success(client):
    # Test successful case
    pass

def test_health_check_failure(client):
    # Test failure case
    pass
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    python run_tests.py all -v
```

## Debugging Tests

### Enable detailed logging:
```bash
pytest -s -vv --log-cli-level=DEBUG
```

### Run specific test with pdb:
```bash
pytest -s --pdb tests/api/test_manifest_endpoints.py::test_execute_manifest_success
```

### Check test marks:
```bash
pytest --markers
```

## Performance Testing

Some tests include performance assertions:

```python
def test_api_response_time(client):
    response = client.get("/api/v1/health")
    assert float(response.headers["X-Process-Time"]) < 0.1
```

## Mocking External Dependencies

Tests use mocking to isolate components:

```python
@patch('dag_engine.loaders.LoaderFactory.get_loader')
def test_with_mock_loader(mock_loader, client):
    mock_loader.return_value.load.return_value = {"test": "data"}
    # Test logic here
```

## Best Practices

1. **Keep tests independent**: Each test should be able to run in isolation
2. **Use fixtures**: Don't repeat setup code
3. **Test edge cases**: Empty inputs, invalid data, concurrent requests
4. **Assert specific values**: Don't just check status codes
5. **Clean up resources**: Ensure tests don't leave artifacts
6. **Document complex tests**: Add docstrings explaining the test scenario