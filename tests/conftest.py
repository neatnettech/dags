"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from typing import Generator
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core import create_app
from api.core.models import Manifest, Step, Prerequisite


@pytest.fixture(scope="session")
def app():
    """Create application instance for testing"""
    return create_app()


@pytest.fixture(scope="function")
def client(app) -> Generator:
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_manifest() -> Manifest:
    """Create a sample manifest for testing"""
    return Manifest(
        id="test-manifest-001",
        creationTimeStamp="2024-01-01T00:00:00Z",
        manifestTemplate="standard",
        processType="data_processing",
        processName="Test Data Load",
        processDate="2024-01-01",
        fileTypesToProcess=[
            Step(
                stepID="step1",
                interfaceType="File_Thomson",
                sourceLocationOld="/old/path/file1.thomson",
                sourceLocationNew="/tests/fixtures/data/new/thomson1.thomson",
                prerequisites=[]
            ),
            Step(
                stepID="step2",
                interfaceType="File_Reuters",
                sourceLocationOld="/old/path/file2.reuters",
                sourceLocationNew="/tests/fixtures/data/new/reuters1.reuters",
                prerequisites=[Prerequisite(stepId="step1")]
            )
        ]
    )


@pytest.fixture
def manifest_with_cyclic_dependency() -> Manifest:
    """Create a manifest with cyclic dependencies"""
    return Manifest(
        id="cyclic-manifest-001",
        creationTimeStamp="2024-01-01T00:00:00Z",
        manifestTemplate="standard",
        processType="data_processing",
        processName="Cyclic Test",
        processDate="2024-01-01",
        fileTypesToProcess=[
            Step(
                stepID="step1",
                interfaceType="File_Thomson",
                sourceLocationOld="/old/path/file1.thomson",
                sourceLocationNew="/new/path/file1.thomson",
                prerequisites=[Prerequisite(stepId="step2")]
            ),
            Step(
                stepID="step2",
                interfaceType="File_Reuters",
                sourceLocationOld="/old/path/file2.reuters",
                sourceLocationNew="/new/path/file2.reuters",
                prerequisites=[Prerequisite(stepId="step1")]
            )
        ]
    )


@pytest.fixture
def manifest_with_invalid_type() -> Manifest:
    """Create a manifest with unsupported interface type"""
    return Manifest(
        id="invalid-type-manifest-001",
        creationTimeStamp="2024-01-01T00:00:00Z",
        manifestTemplate="standard",
        processType="data_processing",
        processName="Invalid Type Test",
        processDate="2024-01-01",
        fileTypesToProcess=[
            Step(
                stepID="step1",
                interfaceType="File_Unknown",
                sourceLocationOld="/old/path/file1.unknown",
                sourceLocationNew="/new/path/file1.unknown",
                prerequisites=[]
            )
        ]
    )


@pytest.fixture
def empty_manifest() -> Manifest:
    """Create an empty manifest"""
    return Manifest(
        id="empty-manifest-001",
        creationTimeStamp="2024-01-01T00:00:00Z",
        manifestTemplate="standard",
        processType="data_processing",
        processName="Empty Test",
        processDate="2024-01-01",
        fileTypesToProcess=[]
    )


@pytest.fixture
def expected_api_response_keys():
    """Expected keys in API response"""
    return {"success", "message", "data", "timestamp", "request_id"}


@pytest.fixture
def expected_error_response_keys():
    """Expected keys in error response"""
    return {"success", "error", "error_code", "message", "timestamp", "request_id"}