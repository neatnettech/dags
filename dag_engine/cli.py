import logging
import click
from .parser import load_manifest
from .executor import DAGExecutor

# configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)

@click.command()
@click.option(
    '--manifest', '-m', required=True,
    help='Path to the DAG manifest JSON file.'
)
@click.option(
    '--log-level', '-l',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default='INFO',
    help='Set the logging level.'
)
def main(manifest: str, log_level: str) -> None:
    """CLI entrypoint for dag-execution-engine."""
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    cfg_manifest = load_manifest(manifest)
    executor = DAGExecutor(cfg_manifest.fileTypesToProcess)
    executor.execute()

if __name__ == '__main__':
    main()