"""Data validation utilities."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from src.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class DataValidator:
    """Validate data integrity and format."""
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = get_logger(self.__class__.__name__)
    
    def validate_gb_data_item(self, data: Dict[str, Any]) -> bool:
        """Validate a single GB data item."""
        try:
            # Check required fields
            required_fields = ["sample_id", "g_id", "author", "title", "sample", "words"]
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate words structure
            words = data.get("words", {})
            if not isinstance(words, dict):
                self.logger.warning("Words field must be a dictionary")
                return False
            
            # Validate word entries
            for word, word_data in words.items():
                if not isinstance(word_data, dict):
                    self.logger.warning(f"Word data for '{word}' must be a dictionary")
                    return False
                
                # Check for required word data fields
                required_word_fields = ["Std", "Prov", "OCR", "i"]
                for field in required_word_fields:
                    if field not in word_data:
                        self.logger.warning(f"Missing required word field '{field}' for word '{word}'")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def validate_gemini_data_item(self, data: Dict[str, Any]) -> bool:
        """Validate a single Gemini data item."""
        try:
            # Check required fields
            if "utterance" not in data:
                self.logger.warning("Missing required field: utterance")
                return False
            
            # Validate utterance is not empty
            utterance = data.get("utterance", "")
            if not utterance or not utterance.strip():
                self.logger.warning("Utterance cannot be empty")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def validate_pattern(self, data: Dict[str, Any]) -> bool:
        """Validate a pattern item."""
        try:
            # Check required fields
            if "label" not in data or "pattern" not in data:
                self.logger.warning("Pattern must have 'label' and 'pattern' fields")
                return False
            
            # Validate pattern structure
            pattern = data.get("pattern", [])
            if not isinstance(pattern, list):
                self.logger.warning("Pattern must be a list")
                return False
            
            # Validate pattern tokens
            for token in pattern:
                if not isinstance(token, dict):
                    self.logger.warning("Pattern tokens must be dictionaries")
                    return False
                
                if "lower" not in token:
                    self.logger.warning("Pattern tokens must have 'lower' field")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
