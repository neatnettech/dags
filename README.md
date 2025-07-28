# DAG Execution Engine

A production-grade Python DAG (Directed Acyclic Graph) execution engine with pluggable executors, comprehensive error handling, and a RESTful API.

## Features

- **DAG Processing**: Parse and execute tasks based on dependencies
- **Dependency Resolution**: Automatic topological sorting with cycle detection
- **Pluggable Architecture**: Extensible executor system for different file types
- **Production API**: FastAPI with comprehensive error handling and request tracking
- **Type Safety**: Full Pydantic validation throughout
- **Monitoring**: Request IDs, timing metrics, and structured logging
- **Testing**: Comprehensive test suite with >80% coverage

## Project Structure

```
.
├── api/                    # FastAPI application
│   ├── core/              # Application configuration
│   ├── exceptions/        # Error handling
│   ├── middleware/        # Request processing
│   ├── models/           # Pydantic models
│   └── routers/          # API endpoints
├── dag_engine/           # Core DAG engine
│   ├── executor.py       # Task execution
│   ├── loaders.py        # File loaders
│   └── models.py         # Domain models
└── tests/                # Test suite
    ├── api/              # API tests
    ├── integration/      # E2E tests
    └── unit/            # Unit tests
```

## Installation

### Prerequisites

- Python 3.11+
- Poetry (dependency management)

### Install Poetry

```bash
# Official installer
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/dag-execution-engine.git
cd dag-execution-engine

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Usage

### Running the API Server

```bash
# Using Poetry script
poetry run dag-api

# Or directly
poetry run python main.py

# Development mode with auto-reload
poetry run uvicorn main:app --reload
```

The API will be available at:
- API endpoints: `http://localhost:8000/api/v1/`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### CLI Usage

```bash
# Run DAG from command line
poetry run dag-engine --manifest path/to/manifest.json --log-level INFO
```

### API Endpoints

All endpoints use the `/api/v1` prefix:

- `GET /api/v1/` - API information
- `GET /api/v1/health` - Health check
- `GET /api/v1/supported-types` - List supported file types
- `POST /api/v1/execute-manifest` - Execute a DAG manifest

### Example Manifest

```json
{
    "id": "example-001",
    "creationTimeStamp": "2024-01-01T00:00:00Z",
    "manifestTemplate": "standard",
    "processType": "data_processing",
    "processName": "Daily ETL",
    "processDate": "2024-01-01",
    "fileTypesToProcess": [
        {
            "stepID": "extract-1",
            "interfaceType": "File_Thomson",
            "sourceLocationOld": "/old/data.thomson",
            "sourceLocationNew": "/new/data.thomson",
            "prerequisites": []
        },
        {
            "stepID": "transform-1",
            "interfaceType": "File_Reuters",
            "sourceLocationOld": "/old/data.reuters",
            "sourceLocationNew": "/new/data.reuters",
            "prerequisites": [{"stepId": "extract-1"}]
        }
    ]
}
```

## Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run specific test suites
poetry run python run_tests.py unit        # Unit tests only
poetry run python run_tests.py api         # API tests only
poetry run python run_tests.py integration # Integration tests only

# Run with verbose output
poetry run pytest -vv

# Run specific test file
poetry run pytest tests/api/test_health_endpoints.py
```

### Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy .

# Linting
poetry run flake8
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

## Configuration

Create a `.env` file for environment-specific settings:

```env
# Application
DEBUG=true
APP_NAME="DAG Execution Engine"
APP_VERSION="1.0.0"

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Logging
LOG_LEVEL=DEBUG

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

## API Response Format

### Success Response

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... },
    "timestamp": "2024-01-01T00:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Response

```json
{
    "success": false,
    "error": "Error Type",
    "error_code": "ERROR_CODE",
    "message": "Detailed error message",
    "timestamp": "2024-01-01T00:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "details": { ... }
}
```

## Error Codes

- `VALIDATION_ERROR` - Request validation failed
- `CYCLIC_DEPENDENCY` - Circular dependency detected
- `MANIFEST_LOAD_ERROR` - Invalid manifest format
- `UNSUPPORTED_INTERFACE_TYPE` - Unknown file type
- `PREREQUISITE_FAILED` - Dependency execution failed
- `EXECUTOR_NOT_FOUND` - Missing executor for type
- `INTERNAL_ERROR` - Unexpected server error

## Docker Support

```bash
# Build image
docker build -t dag-engine .

# Run container
docker run -p 8000:8000 dag-engine
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Piotr Pestka <pp@neatnet.tech>