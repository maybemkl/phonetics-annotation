"""Pattern filtering utilities."""

import re
from typing import List, Set

from .generator import Pattern


class PatternFilter:
    """Filter patterns based on various criteria."""
    
    def __init__(self):
        """Initialize pattern filter."""
        # Common stopwords that should be filtered out
        self.stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "can", "this", "that", "these",
            "those", "i", "you", "he", "she", "it", "we", "they", "me", "him",
            "her", "us", "them", "my", "your", "his", "her", "its", "our", "their"
        }
        
        # Pattern for non-alphanumeric characters
        self.pattern_to_keep = re.compile(r"[^a-zA-Z0-9\s]")
    
    def filter_patterns(self, patterns: List[Pattern], min_length: int = 3) -> List[Pattern]:
        """Filter patterns based on length and stopwords."""
        filtered = []
        seen = set()
        
        for pattern in patterns:
            # Extract the text from the pattern
            pattern_text = " ".join([token.get("lower", "") for token in pattern.pattern])
            
            # Check if pattern meets criteria
            if self._is_valid_pattern(pattern_text, min_length, seen):
                filtered.append(pattern)
                seen.add(pattern_text)
        
        return filtered
    
    def _is_valid_pattern(self, pattern_text: str, min_length: int, seen: Set[str]) -> bool:
        """Check if pattern is valid."""
        if not pattern_text:
            return False
        
        if pattern_text in seen:
            return False
        
        if len(pattern_text) < min_length:
            return False
        
        if pattern_text in self.stopwords:
            return False
        
        return True
    
    def deduplicate_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Remove duplicate patterns."""
        seen = set()
        unique_patterns = []
        
        for pattern in patterns:
            # Create a key for deduplication
            pattern_key = (pattern.label, tuple(token.get("lower", "") for token in pattern.pattern))
            
            if pattern_key not in seen:
                seen.add(pattern_key)
                unique_patterns.append(pattern)
        
        return unique_patterns
