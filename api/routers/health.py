from fastapi import APIRouter, Request, status
import logging
from datetime import datetime

from ..models.responses import APIResponse
from ..exceptions.exceptions import APIException
from ..core.executor import LoaderFactory

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["health"]
)


@router.get("/", response_model=APIResponse)
async def root(request: Request):
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message="DAG Execution API is running",
        data={
            "endpoints": {
                "/api/v1/execute-manifest": "POST - Execute a manifest",
                "/api/v1/supported-types": "GET - Get supported file types",
                "/api/v1/health": "GET - Health check"
            }
        },
        timestamp=datetime.utcnow().isoformat(),
        request_id=getattr(request.state, 'request_id', None)
    )


@router.get("/health", response_model=APIResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={
            "status": "healthy",
            "version": "1.0.0",
            "uptime": "active"
        },
        timestamp=datetime.utcnow().isoformat(),
        request_id=getattr(request.state, 'request_id', None)
    )


@router.get("/supported-types", response_model=APIResponse)
async def get_supported_types(request: Request):
    """Get list of supported file types"""
    try:
        supported_types = LoaderFactory.get_supported_types()
        return APIResponse(
            success=True,
            message="Supported file types retrieved successfully",
            data={"supported_types": supported_types},
            timestamp=datetime.utcnow().isoformat(),
            request_id=getattr(request.state, 'request_id', None)
        )
    except Exception as e:
        logger.error(f"Error retrieving supported types: {str(e)}")
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SUPPORTED_TYPES_ERROR",
            message="Failed to retrieve supported file types"
        )