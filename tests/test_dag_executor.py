import json
import logging

from dag_engine.executor import DAGExecutor, register_executor, StepExecutor
from dag_engine.parser import load_manifest


# Register dummy executors for test types
@register_executor('TypeB')
class DummyExecutorB(StepExecutor):
    def execute(self, step):
        logging.getLogger(__name__).info(f"[TypeB] Dummy execute {step.stepID}")


@register_executor('TypeC')
class DummyExecutorC(StepExecutor):
    def execute(self, step):
        logging.getLogger(__name__).info(f"[TypeC] Dummy execute {step.stepID}")


def test_execution_order_and_logging(tmp_path, caplog):
    sample = json.dumps(
        json.load(open("fixtures/sample_manifest.json")),
        indent=2
    )
    path = tmp_path / "sample.json"
    path.write_text(sample)

    manifest = load_manifest(str(path))
    executor = DAGExecutor(manifest.fileTypesToProcess)

    caplog.set_level(logging.INFO)
    executor.execute()

    assert executor.execution_order == ["A", "B", "C"]

    log_messages = [record.getMessage() for record in caplog.records]

    assert "[EXEC] Running A via TypeA" in log_messages
    assert "[EXEC] Running B via TypeB" in log_messages
    assert "[EXEC] Running C via TypeC" in log_messages
