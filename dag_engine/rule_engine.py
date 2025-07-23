from abc import ABC, abstractmethod
from typing import Dict, Any

class RuleEngine(ABC):
    """Interface for rule evaluation before step execution."""

    @abstractmethod
    def evaluate(self, step_data: Dict[str, Any]) -> bool:
        """Return True if step should run, False to skip."""
        pass

class DefaultRuleEngine(RuleEngine):
    """Default implementation that always passes."""
    def evaluate(self, step_data: Dict[str, Any]) -> bool:
        return True