"""Data loading utilities."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import jsonlines
from pydantic import BaseModel, Field

from ..utils.logging import get_logger

logger = get_logger(__name__)


class GBDataItem(BaseModel):
    """GB data item model."""
    
    sample_id: int
    g_id: str
    author: str
    title: str
    sample: str
    words: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class GeminiDataItem(BaseModel):
    """Gemini data item model."""
    
    utterance: str
    speaker: Optional[str] = None
    speaker_in_char_list: Optional[bool] = None
    addressee: Optional[str] = None
    addressee_in_char_list: Optional[bool] = None


class DataLoader(ABC):
    """Abstract base class for data loaders."""
    
    def __init__(self, file_path: Path):
        """Initialize loader with file path."""
        self.file_path = Path(file_path)
        self.logger = get_logger(self.__class__.__name__)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
    
    @abstractmethod
    def load(self) -> Iterator[Any]:
        """Load data from file."""
        pass
    
    def load_all(self) -> List[Any]:
        """Load all data from file into memory."""
        return list(self.load())


class GBDataLoader(DataLoader):
    """Loader for GB data files."""
    
    def load(self) -> Iterator[GBDataItem]:
        """Load GB data items from JSONL file."""
        self.logger.info(f"Loading GB data from {self.file_path}")
        
        try:
            with jsonlines.open(self.file_path) as reader:
                for line_num, line in enumerate(reader, 1):
                    try:
                        yield GBDataItem(**line)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse line {line_num}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"Failed to load GB data: {e}")
            raise


class GeminiDataLoader(DataLoader):
    """Loader for Gemini data files."""
    
    def load(self) -> Iterator[GeminiDataItem]:
        """Load Gemini data items from JSONL file."""
        self.logger.info(f"Loading Gemini data from {self.file_path}")
        
        try:
            with jsonlines.open(self.file_path) as reader:
                for line_num, line in enumerate(reader, 1):
                    try:
                        yield GeminiDataItem(**line)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse line {line_num}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"Failed to load Gemini data: {e}")
            raise


def create_loader(file_path: Path) -> DataLoader:
    """Create appropriate loader based on file content."""
    # Simple heuristic: check if file contains GB data structure
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            if first_line:
                data = json.loads(first_line)
                if 'sample_id' in data and 'words' in data:
                    return GBDataLoader(file_path)
                elif 'utterance' in data:
                    return GeminiDataLoader(file_path)
    except Exception:
        pass
    
    # Default to GB loader if we can't determine
    return GBDataLoader(file_path)
