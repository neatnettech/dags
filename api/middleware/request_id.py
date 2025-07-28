from fastapi import FastAPI, Request
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_request_id_middleware(app: FastAPI) -> None:
    """Set up request ID and timing middleware"""
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Track request timing
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request completion
        logger.info(
            f"Request {request_id} - {request.method} {request.url.path} "
            f"completed in {process_time:.3f}s with status {response.status_code}"
        )
        
        return response