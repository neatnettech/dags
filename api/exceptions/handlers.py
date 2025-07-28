from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from datetime import datetime

from .exceptions import APIException
from ..models.responses import ErrorResponse
from ..core.exceptions import CyclicDependencyError, ManifestLoadError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up all exception handlers for the FastAPI application"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                error_code=exc.error_code,
                message=exc.detail,
                timestamp=datetime.utcnow().isoformat(),
                request_id=getattr(request.state, 'request_id', None),
                details=exc.details
            ).dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error",
                error_code="VALIDATION_ERROR",
                message="Request validation failed",
                timestamp=datetime.utcnow().isoformat(),
                request_id=getattr(request.state, 'request_id', None),
                details={"validation_errors": exc.errors()}
            ).dict()
        )

    @app.exception_handler(CyclicDependencyError)
    async def cyclic_dependency_exception_handler(request: Request, exc: CyclicDependencyError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="Cyclic Dependency Error",
                error_code="CYCLIC_DEPENDENCY",
                message=str(exc),
                timestamp=datetime.utcnow().isoformat(),
                request_id=getattr(request.state, 'request_id', None)
            ).dict()
        )

    @app.exception_handler(ManifestLoadError)
    async def manifest_load_exception_handler(request: Request, exc: ManifestLoadError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="Manifest Load Error",
                error_code="MANIFEST_LOAD_ERROR",
                message=str(exc),
                timestamp=datetime.utcnow().isoformat(),
                request_id=getattr(request.state, 'request_id', None)
            ).dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                timestamp=datetime.utcnow().isoformat(),
                request_id=getattr(request.state, 'request_id', None),
                details={"trace_id": str(id(exc))} if logger.isEnabledFor(logging.DEBUG) else None
            ).dict()
        )