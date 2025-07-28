"""
Tests for middleware components
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import uuid
from unittest.mock import patch

from api.middleware.request_id import setup_request_id_middleware


class TestRequestIDMiddleware:
    """Test request ID middleware"""
    
    def test_request_id_generation(self, client):
        """Test that request ID is generated for each request"""
        response = client.get("/api/v1/health")
        
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        
        # Verify it's a valid UUID
        uuid_obj = uuid.UUID(request_id)
        assert str(uuid_obj) == request_id
    
    def test_unique_request_ids(self, client):
        """Test that each request gets a unique ID"""
        request_ids = []
        
        for _ in range(5):
            response = client.get("/api/v1/health")
            request_ids.append(response.headers["X-Request-ID"])
        
        # All IDs should be unique
        assert len(set(request_ids)) == len(request_ids)
    
    def test_request_id_in_response_body(self, client):
        """Test that request ID appears in response body"""
        response = client.get("/api/v1/health")
        
        header_id = response.headers["X-Request-ID"]
        body = response.json()
        
        assert body["request_id"] == header_id
    
    def test_process_time_header(self, client):
        """Test that process time is tracked"""
        response = client.get("/api/v1/health")
        
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        
        assert process_time > 0
        assert process_time < 1  # Health check should be fast
    
    def test_middleware_error_handling(self, client):
        """Test middleware handles errors properly"""
        # Even with errors, middleware should add headers
        response = client.post("/api/v1/execute-manifest", json={"invalid": "data"})
        
        assert response.status_code == 422
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
    
    @patch('api.middleware.request_id.logger')
    def test_request_logging(self, mock_logger, client):
        """Test that requests are logged"""
        response = client.get("/api/v1/health")
        
        # Verify logging was called
        mock_logger.info.assert_called()
        
        # Check log message contains expected information
        log_call = mock_logger.info.call_args[0][0]
        assert "GET" in log_call
        assert "/api/v1/health" in log_call
        assert "200" in str(response.status_code)
        assert "completed in" in log_call


class TestMiddlewareIntegration:
    """Test middleware integration with the app"""
    
    def test_middleware_order(self):
        """Test that middleware is applied in correct order"""
        from api.core import create_app
        app = create_app()
        
        # Track middleware execution order
        execution_order = []
        
        @app.middleware("http")
        async def test_middleware(request, call_next):
            execution_order.append("test_before")
            response = await call_next(request)
            execution_order.append("test_after")
            return response
        
        client = TestClient(app)
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        assert len(execution_order) == 2
        assert execution_order[0] == "test_before"
        assert execution_order[1] == "test_after"
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        # Preflight request
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        # Note: access-control-allow-headers might not be present if not needed
    
    def test_cors_actual_request(self, client):
        """Test CORS headers on actual request"""
        response = client.get(
            "/api/v1/health",
            headers={"Origin": "http://example.com"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers