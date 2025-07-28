"""
Core exceptions for DAG execution
"""


class CyclicDependencyError(Exception):
    """Raised when a cycle is detected in the DAG."""
    pass


class ManifestLoadError(Exception):
    """Raised on manifest parsing or validation errors."""
    pass


class ExecutorNotFoundError(Exception):
    """Raised when an executor for a given interface type is not found."""
    pass