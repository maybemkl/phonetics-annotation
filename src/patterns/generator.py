"""Pattern generation logic."""

import re
from pathlib import Path
from typing import Dict, List, Set

import spacy
from pydantic import BaseModel

from config import get_settings
from src.data.loaders import GBDataItem, create_loader
from src.utils.logging import get_logger

logger = get_logger(__name__)


class Pattern(BaseModel):
    """Pattern model for Prodigy."""
    
    label: str
    pattern: List[Dict[str, str]]


class PatternGenerator:
    """Generate patterns from phonetic data."""
    
    def __init__(self):
        """Initialize pattern generator."""
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize spaCy for stopword filtering
        if self.settings.patterns.enable_stopword_filter:
            try:
                self.nlp = spacy.blank("en")
                self.stopwords = self.nlp.Defaults.stop_words
            except Exception as e:
                self.logger.warning(f"Failed to load spaCy stopwords: {e}")
                self.stopwords = set()
        else:
            self.stopwords = set()
        
        # Pattern to keep (non-alphanumeric characters)
        self.pattern_to_keep = re.compile(r"[^a-zA-Z0-9\s]")
        
        # Track seen patterns to avoid duplicates
        self.seen_patterns: Set[str] = set()
    
    def generate_from_gb_data(self, data_file: Path) -> List[Pattern]:
        """Generate patterns from GB data file."""
        self.logger.info(f"Generating patterns from {data_file}")
        
        patterns = []
        kept_count = 0
        
        try:
            loader = create_loader(data_file)
            for item in loader.load():
                if isinstance(item, GBDataItem):
                    item_patterns = self._extract_patterns_from_gb_item(item)
                    patterns.extend(item_patterns)
                    kept_count += len(item_patterns)
            
            self.logger.info(f"Generated {kept_count} patterns from {data_file}")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to generate patterns from {data_file}: {e}")
            raise
    
    def _extract_patterns_from_gb_item(self, item: GBDataItem) -> List[Pattern]:
        """Extract patterns from a single GB data item."""
        patterns = []
        
        # Get words from the item
        words = list(item.words.keys())
        
        for word in words:
            # Create variants (original and cleaned) - match original logic
            variants = {
                word.lower(),
                self.pattern_to_keep.sub("", word.lower())
            }
            
            for variant in variants:
                if self._is_valid_pattern(variant):
                    # Split into tokens and create pattern - match original format
                    tokens = [{"lower": token} for token in variant.split()]
                    pattern = Pattern(
                        label="PHONETIC",
                        pattern=tokens
                    )
                    patterns.append(pattern)
                    self.seen_patterns.add(variant)
        
        return patterns
    
    def _is_valid_pattern(self, pattern: str) -> bool:
        """Check if pattern is valid according to settings."""
        if not pattern:
            return False
        
        if pattern in self.seen_patterns:
            return False
        
        if len(pattern) < self.settings.patterns.min_pattern_length:
            return False
        
        if len(pattern) > self.settings.patterns.max_pattern_length:
            return False
        
        if self.settings.patterns.enable_stopword_filter:
            if pattern in self.stopwords:
                return False
        
        return True
    
    def save_patterns(self, patterns: List[Pattern], output_file: Path) -> None:
        """Save patterns to JSONL file."""
        self.logger.info(f"Saving {len(patterns)} patterns to {output_file}")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for pattern in patterns:
                    f.write(pattern.model_dump_json() + "\n")
            
            self.logger.info(f"Successfully saved patterns to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save patterns to {output_file}: {e}")
            raise
