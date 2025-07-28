#!/usr/bin/env python3
"""
Main entry point for the DAG Execution API

This module provides the main entry point for running the FastAPI application
in both development and production environments.
"""

import uvicorn
from api.core import create_app, settings

# Create the FastAPI application
app = create_app()


def run():
    """Run the FastAPI application - entry point for Poetry script"""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    run()