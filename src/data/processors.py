"""Data processing utilities."""

import re
from typing import Any, Dict, List, Optional

from src.data.loaders import GBDataItem, GeminiDataItem
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Process and transform data."""
    
    def __init__(self):
        """Initialize data processor."""
        self.logger = get_logger(self.__class__.__name__)
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_phonetic_words(self, gb_item: GBDataItem) -> List[str]:
        """Extract phonetic words from a GB data item."""
        words = []
        
        for word, word_data in gb_item.words.items():
            # Only include words that have phonetic variants
            if word_data.get("Std") != word:
                words.append(word)
        
        return words
    
    def normalize_word(self, word: str) -> str:
        """Normalize a word for pattern matching."""
        if not word:
            return ""
        
        # Convert to lowercase
        word = word.lower()
        
        # Remove non-alphanumeric characters except spaces
        word = re.sub(r'[^a-zA-Z0-9\s]', '', word)
        
        # Remove extra whitespace
        word = re.sub(r'\s+', ' ', word).strip()
        
        return word
    
    def split_into_tokens(self, text: str) -> List[str]:
        """Split text into tokens."""
        if not text:
            return []
        
        # Simple tokenization by whitespace
        tokens = text.split()
        
        # Filter out empty tokens
        tokens = [token for token in tokens if token.strip()]
        
        return tokens
    
    def create_prodigy_annotation(self, text: str, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a Prodigy annotation format."""
        return {
            "text": text,
            "spans": spans,
            "meta": {
                "source": "phonetics_annotation"
            }
        }
    
    def merge_annotations(self, annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge multiple annotations."""
        merged = []
        
        for annotation in annotations:
            if annotation not in merged:
                merged.append(annotation)
        
        return merged
