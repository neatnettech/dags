from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .config import settings
from .logging import setup_logging
from ..exceptions import setup_exception_handlers
from ..middleware import setup_request_id_middleware
from ..routers import manifest_router, health_router
from .executor import register_executor, StepExecutor, LoaderFactory
from .models import Step
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def register_custom_executors():
    """Register custom executors that use our loaders"""
    
    @register_executor('File_Thomson')
    class ThomsonExecutor(StepExecutor):
        def execute(self, step: Step) -> Dict[str, Any]:
            logger.info(f"[ThomsonExecutor] Processing {step.stepID}")
            try:
                loader = LoaderFactory.get_loader('File_Thomson')
                result = loader.load(step.sourceLocationNew)
                return result
            except Exception as e:
                logger.error(f"Error in ThomsonExecutor: {str(e)}")
                raise

    @register_executor('File_Reuters')
    class ReutersExecutor(StepExecutor):
        def execute(self, step: Step) -> Dict[str, Any]:
            logger.info(f"[ReutersExecutor] Processing {step.stepID}")
            try:
                loader = LoaderFactory.get_loader('File_Reuters')
                result = loader.load(step.sourceLocationNew)
                return result
            except Exception as e:
                logger.error(f"Error in ReutersExecutor: {str(e)}")
                raise


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Setup logging first
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
        allow_credentials=True,
    )
    
    # Setup middleware
    setup_request_id_middleware(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Register custom executors
    register_custom_executors()
    
    # Include routers
    app.include_router(health_router)
    app.include_router(manifest_router)
    
    logger.info(f"FastAPI application created: {settings.app_name} v{settings.app_version}")
    
    return app