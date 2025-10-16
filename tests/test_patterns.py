"""Tests for pattern generation module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.patterns import PatternGenerator
from src.data.loaders import GBDataItem


class TestPatternGenerator:
    """Test cases for PatternGenerator."""
    
    def test_init(self):
        """Test PatternGenerator initialization."""
        generator = PatternGenerator()
        assert generator.settings is not None
        assert generator.seen_patterns == set()
    
    def test_is_valid_pattern(self):
        """Test pattern validation logic."""
        generator = PatternGenerator()
        
        # Valid patterns
        assert generator._is_valid_pattern("hello") == True
        assert generator._is_valid_pattern("test") == True
        
        # Invalid patterns
        assert generator._is_valid_pattern("") == False
        assert generator._is_valid_pattern("hi") == False  # Too short
        assert generator._is_valid_pattern("a" * 100) == False  # Too long
    
    def test_extract_patterns_from_gb_item(self):
        """Test pattern extraction from GB data item."""
        generator = PatternGenerator()
        
        # Create mock GB data item
        item = GBDataItem(
            sample_id=1,
            g_id="test",
            author="Test Author",
            title="Test Title",
            sample="Test sample",
            words={
                "heben": {"Std": "heaven", "Prov": "CM", "OCR": 0, "i": [1], "multiword": False, "contraction": False, "dtag": "aa"},
                "test": {"Std": "test", "Prov": "CM", "OCR": 0, "i": [2], "multiword": False, "contraction": False, "dtag": "aa"}
            }
        )
        
        patterns = generator._extract_patterns_from_gb_item(item)
        
        # Should extract patterns for both words
        assert len(patterns) == 2
        assert all(pattern.label == "PHONETIC" for pattern in patterns)
        assert all(len(pattern.pattern) == 1 for pattern in patterns)
    
    @patch('src.patterns.generator.create_loader')
    def test_generate_from_gb_data(self, mock_create_loader):
        """Test pattern generation from GB data file."""
        generator = PatternGenerator()
        
        # Mock loader and data
        mock_loader = Mock()
        mock_item = GBDataItem(
            sample_id=1,
            g_id="test",
            author="Test Author", 
            title="Test Title",
            sample="Test sample",
            words={"test": {"Std": "test", "Prov": "CM", "OCR": 0, "i": [1], "multiword": False, "contraction": False, "dtag": "aa"}}
        )
        mock_loader.load.return_value = [mock_item]
        mock_create_loader.return_value = mock_loader
        
        # Test pattern generation
        patterns = generator.generate_from_gb_data(Path("test.jsonl"))
        
        assert len(patterns) == 1
        assert patterns[0].label == "PHONETIC"
        assert patterns[0].pattern[0]["lower"] == "test"
