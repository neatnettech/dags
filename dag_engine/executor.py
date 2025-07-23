import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type
from .models import Step
from .exceptions import CyclicDependencyError
from .rule_engine import RuleEngine, DefaultRuleEngine

logger = logging.getLogger(__name__)

class StepExecutor(ABC):
    """Interface for executing a step."""

    @abstractmethod
    def execute(self, step: Step) -> None:
        pass

_EXECUTOR_REGISTRY: Dict[str, Type[StepExecutor]] = {}


def register_executor(interface_type: str):
    """Decorator to register a StepExecutor implementation."""
    def decorator(cls: Type[StepExecutor]):
        _EXECUTOR_REGISTRY[interface_type] = cls
        return cls
    return decorator


def get_executor(interface_type: str) -> StepExecutor:
    """Factory to retrieve executor instance for an interface type."""
    executor_cls = _EXECUTOR_REGISTRY.get(interface_type)
    if not executor_cls:
        raise ValueError(f"No executor registered for {interface_type}")
    return executor_cls()


@register_executor('TypeA')
class TypeAExecutor(StepExecutor):
    def execute(self, step: Step) -> None:
        logger.info(f"[TypeA] Processing {step.stepID}: {step.sourceLocationOld} -> {step.sourceLocationNew}")


class DAGExecutor:

    def __init__(
        self,
        steps: List[Step],
        rule_engine: RuleEngine = None,
    ):
        self.steps: Dict[str, Step] = {s.stepID: s for s in steps}
        self.graph: Dict[str, List[str]] = self._build_graph()
        self.execution_order: List[str] = []
        self.rule_engine = rule_engine or DefaultRuleEngine()

    def _build_graph(self) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {step_id: [] for step_id in self.steps}
        for step in self.steps.values():
            for pre in step.prerequisites or []:
                if pre.stepId not in self.steps:
                    logger.warning(f"Undefined prerequisite {pre.stepId} for {step.stepID}")
                graph.setdefault(pre.stepId, []).append(step.stepID)
        return graph

    def _visit(self, node: str, temp: Set[str], perm: Set[str]) -> None:
        if node in perm:
            return
        if node in temp:
            raise CyclicDependencyError(f"Cycle detected at '{node}'")
        temp.add(node)
        for child in self.graph.get(node, []):
            self._visit(child, temp, perm)
        temp.remove(node)
        perm.add(node)
        self.execution_order.append(node)

    def resolve_execution_order(self) -> None:
        temp: Set[str] = set()
        perm: Set[str] = set()
        for node in self.graph:
            if node not in perm:
                self._visit(node, temp, perm)
        # convert post-order to topological order
        self.execution_order.reverse()

    def execute(self) -> None:
        """Execute all steps in correct order with rule checks."""
        self.resolve_execution_order()
        for step_id in self.execution_order:
            step = self.steps[step_id]
            if not self.rule_engine.evaluate(step.dict()):
                logger.info(f"[SKIP] Step {step_id} skipped by rules.")
                continue
            executor = get_executor(step.interfaceType)
            logger.info(f"[EXEC] Running {step_id} via {step.interfaceType}")
            executor.execute(step)