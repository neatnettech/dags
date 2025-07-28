"""
Tests for configuration management
"""
import pytest
import os
from unittest.mock import patch

from api.core.config import Settings


class TestConfiguration:
    """Test configuration settings"""
    
    def test_default_settings(self):
        """Test default configuration values"""
        settings = Settings()
        
        assert settings.app_name == "DAG Execution API"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.log_level == "INFO"
        assert settings.api_prefix == "/api/v1"
    
    def test_settings_from_env(self):
        """Test loading settings from environment variables"""
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "HOST": "localhost",
            "PORT": "8080",
            "LOG_LEVEL": "DEBUG"
        }):
            settings = Settings()
            
            assert settings.debug is True
            assert settings.host == "localhost"
            assert settings.port == 8080
            assert settings.log_level == "DEBUG"
    
    def test_cors_settings(self):
        """Test CORS configuration"""
        settings = Settings()
        
        assert settings.allowed_origins == ["*"]
        assert settings.allowed_methods == ["*"]
        assert settings.allowed_headers == ["*"]
    
    def test_custom_cors_settings(self):
        """Test custom CORS configuration from env"""
        with patch.dict(os.environ, {
            "ALLOWED_ORIGINS": '["http://localhost:3000", "https://example.com"]'
        }):
            settings = Settings()
            
            assert "http://localhost:3000" in settings.allowed_origins
            assert "https://example.com" in settings.allowed_origins
    
    def test_case_insensitive_env_vars(self):
        """Test that env vars are case insensitive"""
        with patch.dict(os.environ, {
            "debug": "true",  # lowercase
            "LOG_LEVEL": "DEBUG"  # uppercase
        }):
            settings = Settings()
            
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
    
    def test_invalid_env_values(self):
        """Test handling of invalid environment values"""
        with patch.dict(os.environ, {
            "PORT": "not_a_number",
            "DEBUG": "not_a_boolean"
        }):
            with pytest.raises(ValueError):
                Settings()


class TestLoggingConfiguration:
    """Test logging configuration"""
    
    def test_logging_setup(self):
        """Test logging setup function"""
        from api.core.logging import setup_logging
        import logging
        
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
        
        # Setup logging
        logger = setup_logging()
        
        # Check root logger configuration
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0
        
        # Check handler is StreamHandler
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
    
    def test_logging_format(self):
        """Test logging format"""
        from api.core.logging import setup_logging
        import logging
        
        setup_logging()
        
        # Get the formatter
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter
        
        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Check format contains expected parts
        assert "test" in formatted
        assert "INFO" in formatted
        assert "Test message" in formatted
    
    def test_logger_levels(self):
        """Test specific logger levels"""
        from api.core.logging import setup_logging
        import logging
        
        setup_logging()
        
        # Check uvicorn loggers
        access_logger = logging.getLogger("uvicorn.access")
        error_logger = logging.getLogger("uvicorn.error")
        
        assert access_logger.level == logging.WARNING
        assert error_logger.level == logging.INFO