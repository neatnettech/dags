# Production-Grade FastAPI Project Structure

This directory contains the refactored FastAPI application following production best practices.

## Project Structure

```
api/
├── __init__.py
├── README.md                   # This file
├── core/                       # Core application configuration
│   ├── __init__.py
│   ├── app.py                  # Application factory
│   ├── config.py               # Settings and configuration
│   └── logging.py              # Logging configuration
├── exceptions/                 # Exception handling
│   ├── __init__.py
│   ├── exceptions.py           # Custom exception classes
│   └── handlers.py             # Exception handlers
├── middleware/                 # Custom middleware
│   ├── __init__.py
│   └── request_id.py           # Request ID and timing middleware
├── models/                     # Pydantic models
│   ├── __init__.py
│   ├── requests.py             # Request models
│   └── responses.py            # Response models
└── routers/                    # API route handlers
    ├── __init__.py
    ├── health.py               # Health and utility endpoints
    └── manifest.py             # Manifest execution endpoints
```

## Key Features

### 1. Modular Architecture
- **Separation of Concerns**: Each module has a specific responsibility
- **Scalability**: Easy to add new features and endpoints
- **Maintainability**: Clear organization makes code easier to maintain

### 2. Configuration Management
- **Environment-based**: Settings loaded from environment variables or .env file
- **Type-safe**: Using Pydantic for configuration validation
- **Flexible**: Easy to override settings for different environments

### 3. Exception Handling
- **Centralized**: All exception handlers in one place
- **Consistent**: Unified error response format
- **Production-ready**: Proper HTTP status codes and error messages

### 4. Request/Response Models
- **Type-safe**: Full Pydantic validation
- **Documentation**: Auto-generated OpenAPI docs
- **Consistent**: Standardized response format

### 5. Middleware
- **Request Tracking**: Unique request IDs for tracing
- **Performance Monitoring**: Request timing
- **CORS Support**: Configurable cross-origin policies

## Usage

### Running the Application

```bash
# Using the new main.py
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# For development with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Configuration

Create a `.env` file in the project root:

```env
DEBUG=true
LOG_LEVEL=DEBUG
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### API Endpoints

All endpoints are now prefixed with `/api/v1`:

- `GET /api/v1/` - Root endpoint with API information
- `GET /api/v1/health` - Health check
- `GET /api/v1/supported-types` - Get supported file types
- `POST /api/v1/execute-manifest` - Execute a manifest

### Response Format

All successful responses follow this format:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... },
    "timestamp": "2024-01-01T00:00:00.000Z",
    "request_id": "uuid-string"
}
```

All error responses follow this format:

```json
{
    "success": false,
    "error": "Error Type",
    "error_code": "ERROR_CODE",
    "message": "Detailed error message",
    "timestamp": "2024-01-01T00:00:00.000Z",
    "request_id": "uuid-string",
    "details": { ... }
}
```

## Migration from Legacy app.py

The old `app.py` file has been converted to a backwards-compatibility wrapper. 

**Recommended migration path:**

1. Use `main.py` as the new entry point
2. Import from `api.core.create_app` for programmatic usage
3. Update any deployment scripts to use `main:app` instead of `app:app`

## Error Codes

The API uses structured error codes for different types of failures:

- `VALIDATION_ERROR` - Request validation failed
- `CYCLIC_DEPENDENCY` - Cyclic dependency in DAG
- `MANIFEST_LOAD_ERROR` - Manifest parsing error
- `UNSUPPORTED_INTERFACE_TYPE` - Unsupported file type
- `PREREQUISITE_FAILED` - Step prerequisite failed
- `EXECUTOR_NOT_FOUND` - Missing executor
- `INTERNAL_ERROR` - Unexpected server error

## Development Guidelines

1. **Add new endpoints**: Create routers in `api/routers/`
2. **Add models**: Define in `api/models/requests.py` or `api/models/responses.py`
3. **Custom exceptions**: Add to `api/exceptions/exceptions.py`
4. **Middleware**: Add to `api/middleware/`
5. **Configuration**: Update `api/core/config.py`

## Testing

The modular structure makes testing easier:

```python
from api.core import create_app
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```