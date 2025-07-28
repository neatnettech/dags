"""
Legacy app.py - Backwards compatibility wrapper

This module provides backwards compatibility for the old app.py structure.
For new development, please use the modular structure in the api/ directory.

DEPRECATED: This file is kept for backwards compatibility only.
Use main.py or the api/ module structure for new development.
"""

import warnings
from api.core import create_app

# Issue deprecation warning
warnings.warn(
    "app.py is deprecated. Use main.py or import from api.core.create_app for new development.",
    DeprecationWarning,
    stacklevel=2
)

# Create the app using the new structure
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from api.core.config import settings
    
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )