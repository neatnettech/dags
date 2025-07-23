from pydantic import BaseModel
from typing import List, Optional

class Prerequisite(BaseModel):
    stepId: str

class Step(BaseModel):
    stepID: str
    interfaceType: str
    sourceLocationOld: str
    sourceLocationNew: str
    prerequisites: Optional[List[Prerequisite]] = []

class Manifest(BaseModel):
    id: str
    creationTimeStamp: str
    manifestTemplate: str
    processType: str
    processName: str
    processDate: str
    fileTypesToProcess: List[Step]