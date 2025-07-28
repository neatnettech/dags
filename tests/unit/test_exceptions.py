"""
Tests for exception handling
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.exceptions.exceptions import APIException
from api.core.exceptions import CyclicDependencyError, ManifestLoadError


class TestExceptionHandling:
    """Test exception handling"""
    
    def test_api_exception(self, client):
        """Test APIException handling"""
        # Create a test endpoint that raises APIException
        from api.core import create_app
        app = create_app()
        
        @app.get("/test-api-exception")
        async def test_endpoint():
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="TEST_ERROR",
                message="This is a test error",
                details={"field": "value"}
            )
        
        test_client = TestClient(app)
        response = test_client.get("/test-api-exception")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "TEST_ERROR"
        assert data["message"] == "This is a test error"
        assert data["details"] == {"field": "value"}
    
    def test_cyclic_dependency_exception(self, client, manifest_with_cyclic_dependency):
        """Test CyclicDependencyError handling"""
        response = client.post("/api/v1/execute-manifest", json=manifest_with_cyclic_dependency.dict())
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CYCLIC_DEPENDENCY"
        assert "Cyclic" in data["error"] or "cycle" in data["message"].lower()
    
    def test_manifest_load_exception(self, client):
        """Test ManifestLoadError handling"""
        # Create a test endpoint that raises ManifestLoadError
        from api.core import create_app
        app = create_app()
        
        @app.get("/test-manifest-load-error")
        async def test_endpoint():
            raise ManifestLoadError("Failed to load manifest")
        
        test_client = TestClient(app)
        response = test_client.get("/test-manifest-load-error")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "MANIFEST_LOAD_ERROR"
        assert "Failed to load manifest" in data["message"]
    
    def test_validation_error(self, client):
        """Test validation error handling"""
        # Send invalid data
        response = client.post("/api/v1/execute-manifest", json={"invalid": "data"})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "validation_errors" in data["details"]
        assert isinstance(data["details"]["validation_errors"], list)
    
    def test_general_exception(self, client):
        """Test general exception handling by triggering an actual error"""
        # Use an invalid manifest that will cause an internal error
        invalid_manifest = {
            "id": "test-001",
            "creationTimeStamp": "2024-01-01T00:00:00Z",
            "manifestTemplate": "standard",
            "processType": "test",
            "processName": "Test",
            "processDate": "2024-01-01",
            "fileTypesToProcess": [
                {
                    "stepID": "test-step",
                    "interfaceType": "NonexistentType",  # This will cause an error
                    "sourceLocationOld": "/old/test",
                    "sourceLocationNew": "/new/test",
                    "prerequisites": []
                }
            ]
        }
        
        response = client.post("/api/v1/execute-manifest", json=invalid_manifest)
        
        # This should return 400 for unsupported interface type, not 500
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "UNSUPPORTED_INTERFACE_TYPE"
    
    def test_exception_with_request_id(self, client):
        """Test that exceptions include request ID"""
        response = client.post("/api/v1/execute-manifest", json={"invalid": "data"})
        
        data = response.json()
        assert "request_id" in data
        assert data["request_id"] is not None
        
        # Request ID in response should match header
        assert response.headers["X-Request-ID"] == data["request_id"]
    
    def test_exception_timestamp(self, client):
        """Test that exceptions include timestamp"""
        response = client.post("/api/v1/execute-manifest", json={"invalid": "data"})
        
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"] is not None
        
        # Verify timestamp format (ISO 8601)
        from datetime import datetime
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)


class TestAPIExceptionClass:
    """Test the APIException class itself"""
    
    def test_api_exception_creation(self):
        """Test creating APIException"""
        exc = APIException(
            status_code=400,
            error_code="TEST_ERROR",
            message="Test message",
            details={"key": "value"}
        )
        
        assert exc.status_code == 400
        assert exc.error_code == "TEST_ERROR"
        assert exc.detail == "Test message"
        assert exc.details == {"key": "value"}
    
    def test_api_exception_without_details(self):
        """Test creating APIException without details"""
        exc = APIException(
            status_code=500,
            error_code="SERVER_ERROR",
            message="Server error"
        )
        
        assert exc.status_code == 500
        assert exc.error_code == "SERVER_ERROR"
        assert exc.detail == "Server error"
        assert exc.details is None