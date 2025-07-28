from fastapi import HTTPException
from typing import Dict, Any, Optional


class APIException(HTTPException):
    """Custom API exception with error codes and additional details"""
    
    def __init__(
        self, 
        status_code: int, 
        error_code: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)