from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response model for successful operations"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Standard API response model for error cases"""
    success: bool = False
    error: str
    error_code: str
    message: str
    timestamp: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    uptime: str
    timestamp: str


class SupportedTypesResponse(BaseModel):
    """Supported types response model"""
    supported_types: list[str]


class ExecutionSummary(BaseModel):
    """Execution summary for manifest processing"""
    totalSteps: int
    successfulSteps: int
    failedSteps: int
    overallSuccess: bool


class StepResult(BaseModel):
    """Individual step execution result"""
    stepId: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    executionTime: float
    timestamp: str


class ManifestExecutionResponse(BaseModel):
    """Manifest execution response model"""
    manifestId: str
    processName: str
    processType: str
    execution_summary: ExecutionSummary
    results: list[StepResult]