"""
Tests for API models and validation
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from api.models.responses import (
    APIResponse, ErrorResponse, HealthResponse, 
    SupportedTypesResponse, ExecutionSummary, StepResult,
    ManifestExecutionResponse
)
from api.models.requests import ManifestExecutionRequest
from api.core.models import Manifest, Step, Prerequisite


class TestResponseModels:
    """Test response models"""
    
    def test_api_response_model(self):
        """Test APIResponse model validation"""
        response = APIResponse(
            success=True,
            message="Test message",
            data={"key": "value"},
            timestamp=datetime.utcnow().isoformat(),
            request_id="123e4567-e89b-12d3-a456-426614174000"
        )
        
        assert response.success is True
        assert response.message == "Test message"
        assert response.data == {"key": "value"}
        assert response.request_id is not None
    
    def test_api_response_minimal(self):
        """Test APIResponse with minimal fields"""
        response = APIResponse(
            success=True,
            message="Test",
            timestamp=datetime.utcnow().isoformat()
        )
        
        assert response.success is True
        assert response.data is None
        assert response.request_id is None
    
    def test_error_response_model(self):
        """Test ErrorResponse model validation"""
        response = ErrorResponse(
            error="Test Error",
            error_code="TEST_ERROR",
            message="Test error message",
            timestamp=datetime.utcnow().isoformat(),
            request_id="123e4567-e89b-12d3-a456-426614174000",
            details={"field": "value"}
        )
        
        assert response.success is False
        assert response.error == "Test Error"
        assert response.error_code == "TEST_ERROR"
        assert response.details == {"field": "value"}
    
    def test_health_response_model(self):
        """Test HealthResponse model"""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime="active",
            timestamp=datetime.utcnow().isoformat()
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.uptime == "active"
    
    def test_execution_summary_model(self):
        """Test ExecutionSummary model"""
        summary = ExecutionSummary(
            totalSteps=10,
            successfulSteps=8,
            failedSteps=2,
            overallSuccess=False
        )
        
        assert summary.totalSteps == 10
        assert summary.successfulSteps == 8
        assert summary.failedSteps == 2
        assert summary.overallSuccess is False
    
    def test_step_result_model(self):
        """Test StepResult model"""
        result = StepResult(
            stepId="step1",
            status="success",
            result={"data": "test"},
            executionTime=1.234,
            timestamp=datetime.utcnow().isoformat()
        )
        
        assert result.stepId == "step1"
        assert result.status == "success"
        assert result.result == {"data": "test"}
        assert result.executionTime == 1.234
    
    def test_step_result_with_error(self):
        """Test StepResult model with error"""
        result = StepResult(
            stepId="step1",
            status="failed",
            error="Test error",
            error_type="TestException",
            executionTime=0.5,
            timestamp=datetime.utcnow().isoformat()
        )
        
        assert result.status == "failed"
        assert result.error == "Test error"
        assert result.error_type == "TestException"
        assert result.result is None


class TestRequestModels:
    """Test request models"""
    
    def test_manifest_execution_request(self, sample_manifest):
        """Test ManifestExecutionRequest model"""
        request = ManifestExecutionRequest(manifest=sample_manifest)
        
        assert request.manifest.id == sample_manifest.id
        assert len(request.manifest.fileTypesToProcess) == 2
    
    def test_manifest_model_validation(self):
        """Test Manifest model validation"""
        manifest = Manifest(
            id="test-001",
            creationTimeStamp="2024-01-01T00:00:00Z",
            manifestTemplate="standard",
            processType="batch",
            processName="Test Process",
            processDate="2024-01-01",
            fileTypesToProcess=[]
        )
        
        assert manifest.id == "test-001"
        assert manifest.processType == "batch"
        assert manifest.fileTypesToProcess == []
    
    def test_step_model_validation(self):
        """Test Step model validation"""
        step = Step(
            stepID="step1",
            interfaceType="File_Thomson",
            sourceLocationOld="/old/path",
            sourceLocationNew="/new/path",
            prerequisites=[Prerequisite(stepId="step0")]
        )
        
        assert step.stepID == "step1"
        assert step.interfaceType == "File_Thomson"
        assert len(step.prerequisites) == 1
        assert step.prerequisites[0].stepId == "step0"
    
    def test_step_model_no_prerequisites(self):
        """Test Step model without prerequisites"""
        step = Step(
            stepID="step1",
            interfaceType="File_Thomson",
            sourceLocationOld="/old/path",
            sourceLocationNew="/new/path"
        )
        
        assert step.prerequisites == []
    
    def test_manifest_missing_required_fields(self):
        """Test Manifest validation with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            Manifest(
                id="test-001",
                # Missing required fields
            )
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        required_fields = {error['loc'][0] for error in errors}
        assert 'creationTimeStamp' in required_fields
        assert 'manifestTemplate' in required_fields
    
    def test_step_missing_required_fields(self):
        """Test Step validation with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            Step(
                stepID="step1",
                # Missing required fields
            )
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        required_fields = {error['loc'][0] for error in errors}
        assert 'interfaceType' in required_fields
        assert 'sourceLocationOld' in required_fields
        assert 'sourceLocationNew' in required_fields