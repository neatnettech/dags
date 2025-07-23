import json
from typing import Any
from .models import Manifest
from .exceptions import ManifestLoadError

def load_manifest(path: str) -> Manifest:
    """
    Load and validate the manifest JSON.

    :param path: Path to manifest file
    :raises ManifestLoadError: on parse or validation error
    :return: Manifest instance
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data: Any = json.load(f)
        return Manifest.model_validate(data)
    except Exception as exc:
        raise ManifestLoadError(f"Failed to load manifest: {exc}") from exc