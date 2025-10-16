"""Sampling strategies for balanced data selection."""

import json
import random
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.data.loaders import GBDataItem, GeminiDataItem
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SamplingStrategy(ABC):
    """Abstract base class for sampling strategies."""
    
    def __init__(self, random_seed: Optional[int] = None):
        """Initialize sampling strategy."""
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def sample(self, data: List[Any], sample_size: int) -> List[Any]:
        """Sample data according to the strategy."""
        pass


class RandomSampler(SamplingStrategy):
    """Random sampling strategy."""
    
    def sample(self, data: List[Any], sample_size: int) -> List[Any]:
        """Randomly sample data."""
        if len(data) <= sample_size:
            return data
        
        return random.sample(data, sample_size)


class StratifiedSampler(SamplingStrategy):
    """Stratified sampling strategy for balanced classes."""
    
    def __init__(self, random_seed: Optional[int] = None, patterns_file: Optional[Path] = None, 
                 exceptions_file: Optional[Path] = None):
        """Initialize stratified sampler."""
        super().__init__(random_seed)
        self.logger = get_logger(self.__class__.__name__)
        # Load exceptions first, then patterns (so exceptions can filter patterns)
        self.exceptions = self._load_exceptions(exceptions_file) if exceptions_file else set()
        self.phonetic_patterns = self._load_patterns(patterns_file) if patterns_file else set()
        self.pattern_usage = Counter()  # Track which patterns are used for filtering
    
    def _load_patterns(self, patterns_file: Path) -> Set[str]:
        """Load phonetic patterns from patterns.jsonl file, filtering out exceptions."""
        patterns = set()
        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        pattern_data = json.loads(line)
                        if 'pattern' in pattern_data and pattern_data['pattern']:
                            # Extract the actual pattern text (lowercased)
                            pattern_text = pattern_data['pattern'][0].get('lower', '')
                            if pattern_text and pattern_text not in self.exceptions:
                                patterns.add(pattern_text)
            self.logger.info(f"Loaded {len(patterns)} phonetic patterns from {patterns_file} (filtered from exceptions)")
        except Exception as e:
            self.logger.error(f"Error loading patterns from {patterns_file}: {e}")
        return patterns
    
    def _load_exceptions(self, exceptions_file: Path) -> Set[str]:
        """Load exception words from text file."""
        exceptions = set()
        try:
            with open(exceptions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip comments and empty lines
                        exceptions.add(line.lower())
            self.logger.info(f"Loaded {len(exceptions)} exception words from {exceptions_file}")
        except Exception as e:
            self.logger.error(f"Error loading exceptions from {exceptions_file}: {e}")
        return exceptions
    
    def sample(self, data: List[Any], sample_size: int, 
               dialogue_ratio: float = 0.5) -> List[Any]:
        """Sample data with balanced dialogue/non-dialogue ratio."""
        
        # Separate dialogue and non-dialogue samples
        dialogue_samples = []
        non_dialogue_samples = []
        
        for item in data:
            if self._is_dialogue_sample(item):
                dialogue_samples.append(item)
            else:
                non_dialogue_samples.append(item)
        
        self.logger.info(f"Found {len(dialogue_samples)} dialogue samples")
        self.logger.info(f"Found {len(non_dialogue_samples)} non-dialogue samples")
        
        # Calculate sample sizes for each class
        dialogue_sample_size = int(sample_size * dialogue_ratio)
        non_dialogue_sample_size = sample_size - dialogue_sample_size
        
        # Adjust if we don't have enough samples
        if len(dialogue_samples) < dialogue_sample_size:
            dialogue_sample_size = len(dialogue_samples)
            non_dialogue_sample_size = sample_size - dialogue_sample_size
            self.logger.warning(f"Not enough dialogue samples, using {dialogue_sample_size}")
        
        if len(non_dialogue_samples) < non_dialogue_sample_size:
            non_dialogue_sample_size = len(non_dialogue_samples)
            dialogue_sample_size = sample_size - non_dialogue_sample_size
            self.logger.warning(f"Not enough non-dialogue samples, using {non_dialogue_sample_size}")
        
        # Sample from each class
        sampled_dialogue = random.sample(dialogue_samples, dialogue_sample_size) if dialogue_sample_size > 0 else []
        sampled_non_dialogue = random.sample(non_dialogue_samples, non_dialogue_sample_size) if non_dialogue_sample_size > 0 else []
        
        # Combine samples
        result = sampled_dialogue + sampled_non_dialogue
        
        # Shuffle the result
        random.shuffle(result)
        
        self.logger.info(f"Sampled {len(sampled_dialogue)} dialogue and {len(sampled_non_dialogue)} non-dialogue samples")
        
        return result
    
    def sample_phonetized_dialogue(self, data: List[Any], sample_size: int, 
                                  phonetized_ratio: float = 0.5) -> List[Any]:
        """Sample data with balanced phonetized/non-phonetized dialogue ratio."""
        
        # Separate phonetized and non-phonetized samples
        phonetized_samples = []
        non_phonetized_samples = []
        
        for item in data:
            if self._is_phonetized_sample(item):
                phonetized_samples.append(item)
            else:
                non_phonetized_samples.append(item)
        
        self.logger.info(f"Found {len(phonetized_samples)} phonetized dialogue samples")
        self.logger.info(f"Found {len(non_phonetized_samples)} non-phonetized dialogue samples")
        
        # Calculate sample sizes for each class
        phonetized_sample_size = int(sample_size * phonetized_ratio)
        non_phonetized_sample_size = sample_size - phonetized_sample_size
        
        # Adjust if we don't have enough samples
        if len(phonetized_samples) < phonetized_sample_size:
            phonetized_sample_size = len(phonetized_samples)
            non_phonetized_sample_size = sample_size - phonetized_sample_size
            self.logger.warning(f"Not enough phonetized samples, using {phonetized_sample_size}")
        
        if len(non_phonetized_samples) < non_phonetized_sample_size:
            non_phonetized_sample_size = len(non_phonetized_samples)
            phonetized_sample_size = sample_size - non_phonetized_sample_size
            self.logger.warning(f"Not enough non-phonetized samples, using {non_phonetized_sample_size}")
        
        # Sample from each class
        sampled_phonetized = random.sample(phonetized_samples, phonetized_sample_size) if phonetized_sample_size > 0 else []
        sampled_non_phonetized = random.sample(non_phonetized_samples, non_phonetized_sample_size) if non_phonetized_sample_size > 0 else []
        
        # Combine samples
        result = sampled_phonetized + sampled_non_phonetized
        
        # Shuffle the result
        random.shuffle(result)
        
        self.logger.info(f"Sampled {len(sampled_phonetized)} phonetized and {len(sampled_non_phonetized)} non-phonetized dialogue samples")
        
        return result
    
    def _is_dialogue_sample(self, item: Any) -> bool:
        """Determine if a sample is dialogue or not."""
        if isinstance(item, GBDataItem):
            # For GB data, check if the sample contains dialogue markers
            sample_text = item.sample.lower()
            dialogue_markers = ['"', "'", 'said', 'asked', 'replied', 'answered', 'exclaimed']
            return any(marker in sample_text for marker in dialogue_markers)
        
        elif isinstance(item, GeminiDataItem):
            # Gemini data is already classified as dialogue
            return True
        
        else:
            # Default to non-dialogue for unknown types
            return False
    
    def _is_phonetized_sample(self, item: Any) -> bool:
        """Determine if a sample contains phonetized text using actual patterns."""
        if isinstance(item, GBDataItem):
            # For GB data, check if there are phonetic words
            return len(item.words) > 0
        
        elif isinstance(item, GeminiDataItem):
            # For Gemini data, check if utterance contains any of the loaded phonetic patterns
            utterance = item.utterance.lower()
            # Split into words and check each word against patterns
            words = utterance.split()
            for word in words:
                # Clean word of punctuation for matching
                clean_word = ''.join(c for c in word if c.isalnum() or c in "'-")
                if clean_word in self.phonetic_patterns:
                    # Track pattern usage
                    self.pattern_usage[clean_word] += 1
                    return True
            return False
        
        else:
            # Default to non-phonetized for unknown types
            return False
    
    def save_pattern_usage_stats(self, output_file: Path, phonetized_count: int = None, non_phonetized_count: int = None) -> None:
        """Save pattern usage statistics to a text file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Pattern Usage Statistics\n")
                f.write(f"# Total patterns used: {len(self.pattern_usage)}\n")
                f.write(f"# Total matches: {sum(self.pattern_usage.values())}\n")
                
                # Add sample counts if provided
                if phonetized_count is not None and non_phonetized_count is not None:
                    f.write(f"# Phonetized samples: {phonetized_count}\n")
                    f.write(f"# Non-phonetized samples: {non_phonetized_count}\n")
                    f.write(f"# Total samples: {phonetized_count + non_phonetized_count}\n")
                    f.write(f"# Phonetized ratio: {phonetized_count / (phonetized_count + non_phonetized_count):.3f}\n")
                
                f.write("\n")
                
                # Sort by usage count (descending)
                for pattern, count in self.pattern_usage.most_common():
                    f.write(f"{pattern}: {count}\n")
            
            self.logger.info(f"Pattern usage statistics saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving pattern usage statistics: {e}")


class WeightedSampler(SamplingStrategy):
    """Weighted sampling strategy based on data characteristics."""
    
    def __init__(self, weights: Dict[str, float], random_seed: Optional[int] = None):
        """Initialize weighted sampler with class weights."""
        super().__init__(random_seed)
        self.weights = weights
        self.logger = get_logger(self.__class__.__name__)
    
    def sample(self, data: List[Any], sample_size: int) -> List[Any]:
        """Sample data using weighted selection."""
        if not data:
            return []
        
        # Calculate weights for each item
        item_weights = []
        for item in data:
            weight = self._calculate_weight(item)
            item_weights.append(weight)
        
        # Normalize weights
        total_weight = sum(item_weights)
        if total_weight == 0:
            return random.sample(data, min(sample_size, len(data)))
        
        normalized_weights = [w / total_weight for w in item_weights]
        
        # Sample using weighted selection
        return random.choices(data, weights=normalized_weights, k=min(sample_size, len(data)))
    
    def _calculate_weight(self, item: Any) -> float:
        """Calculate weight for an item based on its characteristics."""
        if isinstance(item, GBDataItem):
            # Weight based on number of phonetic words
            phonetic_count = len([w for w in item.words.keys() if item.words[w].get("Std") != w])
            return self.weights.get("phonetic_density", 1.0) * (phonetic_count + 1)
        
        elif isinstance(item, GeminiDataItem):
            # Weight based on utterance length
            utterance_length = len(item.utterance.split())
            return self.weights.get("utterance_length", 1.0) * utterance_length
        
        return 1.0
