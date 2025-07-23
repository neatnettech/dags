import argparse
from .parser import load_manifest
from .executor import DAGExecutor


def main():
    parser = argparse.ArgumentParser(description="Run DAG executor on a manifest.")
    parser.add_argument(
        "--manifest", required=True,
        help="Path to manifest JSON file"
    )
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    executor = DAGExecutor(manifest.fileTypesToProcess)
    executor.execute()


if __name__ == "__main__":
    main()