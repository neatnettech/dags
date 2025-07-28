"""
Tests for health and utility endpoints
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health and utility endpoints"""
    
    def test_root_endpoint(self, client, expected_api_response_keys):
        """Test root endpoint returns API information"""
        response = client.get("/api/v1/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert set(data.keys()) == expected_api_response_keys
        assert data["success"] is True
        assert "DAG Execution API is running" in data["message"]
        assert "endpoints" in data["data"]
        assert "/api/v1/execute-manifest" in data["data"]["endpoints"]
        assert "/api/v1/supported-types" in data["data"]["endpoints"]
        assert "/api/v1/health" in data["data"]["endpoints"]
    
    def test_health_check(self, client, expected_api_response_keys):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert set(data.keys()) == expected_api_response_keys
        assert data["success"] is True
        assert data["message"] == "Service is healthy"
        assert data["data"]["status"] == "healthy"
        assert data["data"]["version"] == "1.0.0"
    
    def test_supported_types(self, client, expected_api_response_keys):
        """Test supported types endpoint"""
        response = client.get("/api/v1/supported-types")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert set(data.keys()) == expected_api_response_keys
        assert data["success"] is True
        assert "supported_types" in data["data"]
        assert isinstance(data["data"]["supported_types"], list)
        assert "File_Thomson" in data["data"]["supported_types"]
        assert "File_Reuters" in data["data"]["supported_types"]
    
    def test_request_id_header(self, client):
        """Test that request ID header is present"""
        response = client.get("/api/v1/health")
        
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 36  # UUID length
        
    def test_process_time_header(self, client):
        """Test that process time header is present"""
        response = client.get("/api/v1/health")
        
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time > 0
        assert process_time < 1  # Should be fast
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Test-Header"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers