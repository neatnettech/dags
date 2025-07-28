from pydantic import BaseModel, Field
from typing import Optional
from ..core.models import Manifest


class ManifestExecutionRequest(BaseModel):
    """Request model for manifest execution"""
    manifest: Manifest = Field(..., description="The manifest to execute")
    
    class Config:
        schema_extra = {
            "example": {
                "manifest": {
                    "id": "manifest-001",
                    "creationTimeStamp": "2024-01-01T00:00:00Z",
                    "manifestTemplate": "standard",
                    "processType": "data_processing",
                    "processName": "Daily Data Load",
                    "processDate": "2024-01-01",
                    "fileTypesToProcess": [
                        {
                            "stepID": "step1",
                            "interfaceType": "File_Thomson",
                            "sourceLocationOld": "/old/path/file1.thomson",
                            "sourceLocationNew": "/new/path/file1.thomson",
                            "prerequisites": []
                        }
                    ]
                }
            }
        }