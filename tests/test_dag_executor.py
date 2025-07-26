import json
import logging
import pytest
from unittest.mock import patch
from dag_engine.executor import register_executor, StepExecutor
from dag_engine.loaders import LoaderFactory

# Register loader-based executors for integration testing
@register_executor('File_Thomson')
class ThomsonTestExecutor(StepExecutor):
    def execute(self, step):
        loader = LoaderFactory.get_loader('File_Thomson')
        return loader.load(step.sourceLocationNew)


@register_executor('File_Reuters')
class ReutersTestExecutor(StepExecutor):
    def execute(self, step):
        loader = LoaderFactory.get_loader('File_Reuters')
        return loader.load(step.sourceLocationNew)


def test_loader_factory():
    """Test loader factory can resolve correct loaders"""
    # Test Thomson loader
    thomson_loader = LoaderFactory.get_loader("File_Thomson")
    assert thomson_loader is not None
    assert thomson_loader.supported_extensions == ['.thomson', '.tms']
    
    # Test Reuters loader
    reuters_loader = LoaderFactory.get_loader("File_Reuters")
    assert reuters_loader is not None
    assert reuters_loader.supported_extensions == ['.reuters', '.rtr', '.reut']
    
    # Test supported types
    supported = LoaderFactory.get_supported_types()
    assert "File_Thomson" in supported
    assert "File_Reuters" in supported
    
    # Test invalid type
    with pytest.raises(ValueError, match="No loader registered for file type: Invalid_Type"):
        LoaderFactory.get_loader("Invalid_Type")


def test_loader_execution_with_mock_files(tmp_path, caplog):
    """Test loader execution with mock files"""
    # Create mock files
    thomson_file = tmp_path / "test.thomson"
    thomson_file.write_text("Mock Thomson data")
    
    reuters_file = tmp_path / "test.reuters"
    reuters_file.write_text("Mock Reuters data")
    
    # Test Thomson loader
    thomson_loader = LoaderFactory.get_loader("File_Thomson")
    result = thomson_loader.load(str(thomson_file))
    
    assert result["loader"] == "ThomsonLoader"
    assert result["status"] == "loaded"
    assert result["file_path"] == str(thomson_file)
    assert "Thomson" in result["data"]["format"]
    
    # Test Reuters loader
    reuters_loader = LoaderFactory.get_loader("File_Reuters")
    result = reuters_loader.load(str(reuters_file))
    
    assert result["loader"] == "ReutersLoader"
    assert result["status"] == "loaded"
    assert result["file_path"] == str(reuters_file)
    assert "Reuters" in result["data"]["format"]
    
    # Check logging
    caplog.set_level(logging.INFO)
    thomson_loader.load(str(thomson_file))
    
    log_messages = [record.getMessage() for record in caplog.records]
    assert any("ThomsonLoader: Starting to load file" in msg for msg in log_messages)
    assert any("ThomsonLoader: Successfully loaded" in msg for msg in log_messages)


def test_loader_validation():
    """Test loader file validation"""
    thomson_loader = LoaderFactory.get_loader("File_Thomson")
    
    # Test non-existent file
    assert thomson_loader.validate("/non/existent/file.thomson") is False
    
    # Test wrong extension
    with patch('pathlib.Path.exists', return_value=True):
        assert thomson_loader.validate("/some/file.txt") is False
        assert thomson_loader.validate("/some/file.thomson") is True

