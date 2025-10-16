"""Prodigy data formatting utilities."""

from typing import Any, Dict, List, Optional

from src.data.loaders import GBDataItem, GeminiDataItem
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProdigyFormatter:
    """Format data for Prodigy annotation."""
    
    def __init__(self):
        """Initialize Prodigy formatter."""
        self.logger = get_logger(self.__class__.__name__)
    
    def format_gb_data(self, gb_item: GBDataItem, is_dialogue: bool = False) -> Dict[str, Any]:
        """Format GB data item for Prodigy."""
        return {
            "text": gb_item.sample,
            "meta": {
                "source": "gb_data",
                "sample_id": gb_item.sample_id,
                "g_id": gb_item.g_id,
                "author": gb_item.author,
                "title": gb_item.title,
                "book": gb_item.title,  # Use title as book identifier
                "words": gb_item.words,
                "is_dialogue": is_dialogue,
                "phonetic_words": self._extract_phonetic_words(gb_item.words)
            }
        }
    
    def format_gemini_data(self, gemini_item: GeminiDataItem, is_phonetized: bool = False) -> Dict[str, Any]:
        """Format Gemini data item for Prodigy."""
        return {
            "text": gemini_item.utterance,
            "meta": {
                "source": "gemini_data",
                "source_file": gemini_item.source_file,
                "speaker": gemini_item.speaker,
                "speaker_in_char_list": gemini_item.speaker_in_char_list,
                "addressee": gemini_item.addressee,
                "addressee_in_char_list": gemini_item.addressee_in_char_list,
                "is_dialogue": True,  # Gemini data is always dialogue
                "is_phonetized": is_phonetized
            }
        }
    
    def format_mixed_data(self, gb_items: List[GBDataItem], 
                         gemini_items: List[GeminiDataItem]) -> List[Dict[str, Any]]:
        """Format mixed data sources for Prodigy."""
        formatted_items = []
        
        # Format GB items (non-dialogue)
        for gb_item in gb_items:
            formatted_item = self.format_gb_data(gb_item, is_dialogue=False)
            formatted_items.append(formatted_item)
        
        # Format Gemini items (dialogue)
        for gemini_item in gemini_items:
            formatted_item = self.format_gemini_data(gemini_item)
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def _extract_phonetic_words(self, words: Dict[str, Any]) -> List[str]:
        """Extract phonetic words from GB data."""
        phonetic_words = []
        
        for word, word_data in words.items():
            # Check if this is a phonetic variant
            if word_data.get("Std") != word:
                phonetic_words.append(word)
        
        return phonetic_words
    
    def add_annotation_metadata(self, item: Dict[str, Any], 
                               annotation_type: str = "phonetic") -> Dict[str, Any]:
        """Add metadata for annotation tracking."""
        if "meta" not in item:
            item["meta"] = {}
        
        item["meta"]["annotation_type"] = annotation_type
        item["meta"]["annotation_status"] = "pending"
        item["meta"]["created_at"] = self._get_timestamp()
        
        return item
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_prodigy_format(self, item: Dict[str, Any]) -> bool:
        """Validate that item is in correct Prodigy format."""
        required_fields = ["text", "meta"]
        
        for field in required_fields:
            if field not in item:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        if not isinstance(item["text"], str):
            self.logger.warning("Text field must be a string")
            return False
        
        if not isinstance(item["meta"], dict):
            self.logger.warning("Meta field must be a dictionary")
            return False
        
        return True
