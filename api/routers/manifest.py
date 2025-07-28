from fastapi import APIRouter, Request, status
import logging
from datetime import datetime

from ..models.responses import APIResponse, ExecutionSummary, StepResult, ManifestExecutionResponse
from ..exceptions.exceptions import APIException
from ..core.models import Manifest
from ..core.executor import DAGExecutor, get_executor, LoaderFactory
from ..core.exceptions import CyclicDependencyError, ManifestLoadError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["manifest"]
)


@router.post("/execute-manifest", response_model=APIResponse)
async def execute_manifest(manifest: Manifest, request: Request):
    """
    Execute a manifest with DAG steps
    
    The manifest should contain:
    - id: Unique identifier
    - steps: List of steps with file types and dependencies
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        # Input validation
        if not manifest.id:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_MANIFEST_ID",
                message="Manifest ID is required"
            )
        
        if not manifest.fileTypesToProcess:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="NO_STEPS_PROVIDED",
                message="At least one processing step is required"
            )
        
        logger.info(f"[{request_id}] Received manifest: {manifest.id}")
        logger.info(f"[{request_id}] Process: {manifest.processName} ({manifest.processType})")
        logger.info(f"[{request_id}] Total steps: {len(manifest.fileTypesToProcess)}")
        
        # Validate all steps have supported interface types
        supported_types = LoaderFactory.get_supported_types()
        for step in manifest.fileTypesToProcess:
            if step.interfaceType not in supported_types:
                raise APIException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code="UNSUPPORTED_INTERFACE_TYPE",
                    message=f"Interface type '{step.interfaceType}' is not supported",
                    details={
                        "step_id": step.stepID,
                        "interface_type": step.interfaceType,
                        "supported_types": supported_types
                    }
                )
        
        # Create DAG executor with the steps
        try:
            dag_executor = DAGExecutor(steps=manifest.fileTypesToProcess)
            dag_executor.resolve_execution_order()
        except CyclicDependencyError as e:
            logger.error(f"[{request_id}] Cyclic dependency detected: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"[{request_id}] Error creating DAG executor: {str(e)}")
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="DAG_CREATION_ERROR",
                message="Failed to create DAG executor",
                details={"error": str(e)}
            )
        
        # Execute the DAG
        execution_results = []
        failed_steps = 0
        
        for step_id in dag_executor.execution_order:
            step = dag_executor.steps[step_id]
            step_start_time = datetime.utcnow()
            
            try:
                logger.info(f"[{request_id}] Executing step: {step_id}")
                
                # Check if prerequisites failed
                if step.prerequisites:
                    failed_prereqs = [
                        result for result in execution_results 
                        if result["stepId"] in [p.stepId for p in step.prerequisites] 
                        and result["status"] == "failed"
                    ]
                    if failed_prereqs:
                        raise APIException(
                            status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            error_code="PREREQUISITE_FAILED",
                            message=f"Prerequisites failed for step {step_id}",
                            details={"failed_prerequisites": [r["stepId"] for r in failed_prereqs]}
                        )
                
                # Get and execute the step
                try:
                    executor = get_executor(step.interfaceType)
                except Exception as e:
                    # Handle both ExecutorNotFoundError and KeyError
                    error_name = type(e).__name__
                    if error_name == "ExecutorNotFoundError" or "not found" in str(e).lower() or error_name == "KeyError":
                        raise APIException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            error_code="EXECUTOR_NOT_FOUND",
                            message=f"No executor found for interface type: {step.interfaceType}"
                        )
                    raise
                
                result = executor.execute(step)
                execution_time = (datetime.utcnow() - step_start_time).total_seconds()
                
                execution_results.append({
                    "stepId": step_id,
                    "status": "success",
                    "result": result,
                    "executionTime": execution_time,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"[{request_id}] Step {step_id} completed successfully in {execution_time:.3f}s")
                
            except APIException:
                raise
            except Exception as e:
                failed_steps += 1
                execution_time = (datetime.utcnow() - step_start_time).total_seconds()
                error_msg = str(e)
                
                logger.error(f"[{request_id}] Error executing step {step_id}: {error_msg}")
                
                execution_results.append({
                    "stepId": step_id,
                    "status": "failed",
                    "error": error_msg,
                    "error_type": type(e).__name__,
                    "executionTime": execution_time,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Prepare final response
        total_steps = len(manifest.fileTypesToProcess)
        success_count = total_steps - failed_steps
        overall_success = failed_steps == 0
        
        response_data = ManifestExecutionResponse(
            manifestId=manifest.id,
            processName=manifest.processName,
            processType=manifest.processType,
            execution_summary=ExecutionSummary(
                totalSteps=total_steps,
                successfulSteps=success_count,
                failedSteps=failed_steps,
                overallSuccess=overall_success
            ),
            results=[StepResult(**result) for result in execution_results]
        )
        
        message = "Manifest executed successfully" if overall_success else f"Manifest executed with {failed_steps} failed steps"
        
        logger.info(f"[{request_id}] Manifest execution completed. Success: {overall_success}, Failed steps: {failed_steps}")
        
        return APIResponse(
            success=overall_success,
            message=message,
            data=response_data.dict(),
            timestamp=datetime.utcnow().isoformat(),
            request_id=request_id
        )
        
    except APIException:
        raise
    except CyclicDependencyError:
        raise
    except ManifestLoadError:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error processing manifest: {str(e)}", exc_info=True)
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="MANIFEST_EXECUTION_ERROR",
            message="An unexpected error occurred during manifest execution",
            details={"trace_id": str(id(e))} if logger.isEnabledFor(logging.DEBUG) else None
        )