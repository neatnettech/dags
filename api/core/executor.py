"""
DAG execution system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from collections import defaultdict, deque

from .models import Step, Manifest
from .exceptions import CyclicDependencyError, ExecutorNotFoundError

logger = logging.getLogger(__name__)

# Registry for executors
_executors: Dict[str, 'StepExecutor'] = {}


class StepExecutor(ABC):
    """Abstract base class for step executors"""
    
    @abstractmethod
    def execute(self, step: Step) -> Dict[str, Any]:
        """Execute a step and return results"""
        pass


def register_executor(interface_type: str):
    """Decorator to register an executor for an interface type"""
    def decorator(executor_class):
        _executors[interface_type] = executor_class()
        return executor_class
    return decorator


def get_executor(interface_type: str) -> StepExecutor:
    """Get an executor for the given interface type"""
    if interface_type not in _executors:
        raise ExecutorNotFoundError(f"No executor found for interface type: {interface_type}")
    return _executors[interface_type]


class DAGExecutor:
    """Executes steps in a DAG with dependency resolution"""
    
    def __init__(self, steps: List[Step]):
        self.steps = {step.stepID: step for step in steps}
        self.execution_order: List[str] = []
    
    def resolve_execution_order(self):
        """Resolve the execution order using topological sort"""
        # Build dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize all steps
        for step_id in self.steps:
            in_degree[step_id] = 0
        
        # Build graph and calculate in-degrees
        for step in self.steps.values():
            for prereq in step.prerequisites:
                if prereq.stepId not in self.steps:
                    raise CyclicDependencyError(f"Prerequisite {prereq.stepId} not found in steps")
                graph[prereq.stepId].append(step.stepID)
                in_degree[step.stepID] += 1
        
        # Topological sort using Kahn's algorithm
        queue = deque([step_id for step_id in self.steps if in_degree[step_id] == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(self.steps):
            raise CyclicDependencyError("Cyclic dependency detected in the DAG")
        
        self.execution_order = execution_order


class LoaderFactory:
    """Factory for file loaders (mock implementation)"""
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported file types"""
        return ["File_Thomson", "File_Reuters"]
    
    @staticmethod
    def get_loader(loader_type: str):
        """Get a loader for the given type (mock implementation)"""
        if loader_type not in LoaderFactory.get_supported_types():
            raise ValueError(f"Unsupported loader type: {loader_type}")
        
        class MockLoader:
            def load(self, file_path: str) -> Dict[str, Any]:
                # Mock implementation - in real app this would load and process files
                return {
                    "status": "loaded",
                    "file_path": file_path,
                    "loader_type": loader_type,
                    "data": f"Mock data from {loader_type}"
                }
        
        return MockLoader()