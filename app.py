from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dag_engine.models import Manifest, Step
from dag_engine.executor import DAGExecutor, StepExecutor, register_executor, get_executor
from dag_engine.loaders import LoaderFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="DAG Execution API", version="1.0.0")


# Register custom executors that use our loaders
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


@app.get("/")
async def root():
    return {
        "message": "DAG Execution API",
        "endpoints": {
            "/execute-manifest": "POST - Execute a manifest",
            "/supported-types": "GET - Get supported file types"
        }
    }


@app.get("/supported-types")
async def get_supported_types():
    """Get list of supported file types"""
    return {
        "supported_types": LoaderFactory.get_supported_types()
    }


@app.post("/execute-manifest")
async def execute_manifest(manifest: Manifest):
    """
    Execute a manifest with DAG steps
    
    The manifest should contain:
    - id: Unique identifier
    - steps: List of steps with file types and dependencies
    """
    try:
        logger.info(f"Received manifest: {manifest.id}")
        logger.info(f"Process: {manifest.processName} ({manifest.processType})")
        logger.info(f"Total steps: {len(manifest.fileTypesToProcess)}")
        
        # Create DAG executor with the steps
        dag_executor = DAGExecutor(steps=manifest.fileTypesToProcess)
        
        # Execute the DAG
        execution_results = []
        dag_executor.resolve_execution_order()
        
        for step_id in dag_executor.execution_order:
            step = dag_executor.steps[step_id]
            try:
                logger.info(f"Executing step: {step_id}")
                
                # Use our custom executors that integrate with loaders
                executor = get_executor(step.interfaceType)
                result = executor.execute(step)
                
                execution_results.append({
                    "stepId": step_id,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Error executing step {step_id}: {str(e)}")
                execution_results.append({
                    "stepId": step_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Prepare response
        response = {
            "manifestId": manifest.id,
            "processName": manifest.processName,
            "processType": manifest.processType,
            "totalSteps": len(manifest.fileTypesToProcess),
            "executedSteps": len(execution_results),
            "success": all(r["status"] == "success" for r in execution_results),
            "results": execution_results
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error processing manifest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)