from abc import ABC, abstractmethod
import logging
from typing import Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Abstract base class for all file loaders"""
    
    @abstractmethod
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load and process a file
        
        Args:
            file_path: Path to the file to be loaded
            
        Returns:
            Dict containing the loaded data and metadata
        """
        pass
    
    @abstractmethod
    def validate(self, file_path: str) -> bool:
        """Validate if the file can be processed by this loader
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file can be processed, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """List of file extensions supported by this loader"""
        pass


class ThomsonLoader(BaseLoader):
    """Loader for Thomson file format"""
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['.thomson', '.tms']
    
    def validate(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"ThomsonLoader: File not found: {file_path}")
            return False
        
        if path.suffix.lower() not in self.supported_extensions:
            logger.error(f"ThomsonLoader: Unsupported file extension: {path.suffix}")
            return False
            
        logger.info(f"ThomsonLoader: File validation successful for {file_path}")
        return True
    
    def load(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"ThomsonLoader: Starting to load file: {file_path}")
        
        if not self.validate(file_path):
            raise ValueError(f"Invalid file for ThomsonLoader: {file_path}")
        
        # Mock implementation
        logger.info(f"ThomsonLoader: Reading Thomson format data from {file_path}")
        logger.info("ThomsonLoader: Parsing Thomson headers...")
        logger.info("ThomsonLoader: Extracting Thomson metadata...")
        logger.info("ThomsonLoader: Processing Thomson data blocks...")
        
        result = {
            "loader": "ThomsonLoader",
            "file_path": file_path,
            "status": "loaded",
            "data": {
                "mock_data": "Thomson file content would be here",
                "format": "Thomson",
                "records": 100  # Mock record count
            },
            "metadata": {
                "version": "1.0",
                "encoding": "UTF-8"
            }
        }
        
        logger.info(f"ThomsonLoader: Successfully loaded {file_path}")
        return result


class ReutersLoader(BaseLoader):
    """Loader for Reuters file format"""
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['.reuters', '.rtr', '.reut']
    
    def validate(self, file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"ReutersLoader: File not found: {file_path}")
            return False
        
        if path.suffix.lower() not in self.supported_extensions:
            logger.error(f"ReutersLoader: Unsupported file extension: {path.suffix}")
            return False
            
        logger.info(f"ReutersLoader: File validation successful for {file_path}")
        return True
    
    def load(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"ReutersLoader: Starting to load file: {file_path}")
        
        if not self.validate(file_path):
            raise ValueError(f"Invalid file for ReutersLoader: {file_path}")
        
        # Mock implementation
        logger.info(f"ReutersLoader: Reading Reuters data from {file_path}")
        logger.info("ReutersLoader: Parsing Reuters headers...")
        logger.info("ReutersLoader: Extracting Reuters metadata...")
        logger.info("ReutersLoader: Processing Reuters data blocks...")
        logger.info("ReutersLoader: Validating Reuters format...")
        
        result = {
            "loader": "ReutersLoader",
            "file_path": file_path,
            "status": "loaded",
            "data": {
                "mock_data": "Reuters file content would be here",
                "format": "Reuters",
                "records": 75,  # Mock record count
                "articles": 25  # Mock article count
            },
            "metadata": {
                "reuters_type": "News Feed",
                "version": "2.0"
            }
        }
        
        logger.info(f"ReutersLoader: Successfully loaded {file_path}")
        return result


class LoaderFactory:
    """Factory class to create appropriate loader based on file type"""
    
    _loaders = {
        "File_Thomson": ThomsonLoader,
        "File_Reuters": ReutersLoader,
    }
    
    @classmethod
    def register_loader(cls, file_type: str, loader_class: type[BaseLoader]):
        """Register a new loader for a specific file type
        
        Args:
            file_type: The file type identifier
            loader_class: The loader class to use for this file type
        """
        logger.info(f"LoaderFactory: Registering loader {loader_class.__name__} for type {file_type}")
        cls._loaders[file_type] = loader_class
    
    @classmethod
    def get_loader(cls, file_type: str) -> BaseLoader:
        """Get the appropriate loader instance for a file type
        
        Args:
            file_type: The file type identifier
            
        Returns:
            Instance of the appropriate loader
            
        Raises:
            ValueError: If no loader is registered for the file type
        """
        logger.info(f"LoaderFactory: Resolving loader for file type: {file_type}")
        
        if file_type not in cls._loaders:
            available_types = ", ".join(cls._loaders.keys())
            logger.error(f"LoaderFactory: No loader found for type {file_type}. Available types: {available_types}")
            raise ValueError(f"No loader registered for file type: {file_type}")
        
        loader_class = cls._loaders[file_type]
        logger.info(f"LoaderFactory: Creating instance of {loader_class.__name__} for type {file_type}")
        return loader_class()
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of all supported file types"""
        return list(cls._loaders.keys())