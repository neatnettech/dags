"""
Core domain models for DAG execution
"""
from pydantic import BaseModel
from typing import List, Optional


class Prerequisite(BaseModel):
    """A prerequisite step dependency"""
    stepId: str


class Step(BaseModel):
    """A step in the DAG execution"""
    stepID: str
    interfaceType: str
    sourceLocationOld: str
    sourceLocationNew: str
    prerequisites: Optional[List[Prerequisite]] = []


class Manifest(BaseModel):
    """A manifest containing steps to be executed"""
    id: str
    creationTimeStamp: str
    manifestTemplate: str
    processType: str
    processName: str
    processDate: str
    fileTypesToProcess: List[Step]