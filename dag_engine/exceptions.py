class CyclicDependencyError(Exception):
    """Raised when a cycle is detected in the DAG."""
    pass

class ManifestLoadError(Exception):
    """Raised on manifest parsing or validation errors."""
    pass