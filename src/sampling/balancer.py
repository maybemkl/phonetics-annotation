"""Data balancing utilities for 50/50 splits."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.data.loaders import GBDataLoader, GeminiDataLoader, create_loader
from src.sampling.strategies import StratifiedSampler, RandomSampler
from src.prodigy.formatter import ProdigyFormatter
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DataBalancer:
    """Balance data for 50/50 dialogue/non-dialogue splits."""
    
    def __init__(self, random_seed: Optional[int] = None, patterns_file: Optional[Path] = None):
        """Initialize data balancer."""
        self.random_seed = random_seed
        self.logger = get_logger(self.__class__.__name__)
        self.sampler = StratifiedSampler(random_seed=random_seed, patterns_file=patterns_file)
        self.formatter = ProdigyFormatter()
    
    def balance_gb_data(self, data_file: Path, sample_size: int, 
                       dialogue_ratio: float = 0.5) -> List[Any]:
        """Balance GB data with specified dialogue ratio."""
        self.logger.info(f"Balancing GB data from {data_file}")
        
        # Load data
        loader = create_loader(data_file)
        data = list(loader.load())
        
        self.logger.info(f"Loaded {len(data)} items from {data_file}")
        
        # Sample with balanced ratio
        balanced_data = self.sampler.sample(data, sample_size, dialogue_ratio)
        
        self.logger.info(f"Balanced sample contains {len(balanced_data)} items")
        
        return balanced_data
    
    def balance_gemini_data(self, data_files: List[Path], sample_size: int,
                           phonetized_ratio: float = 0.5) -> List[Any]:
        """Balance Gemini data with specified phonetized/non-phonetized ratio."""
        self.logger.info(f"Balancing Gemini data from {len(data_files)} files")
        
        # Load all data
        all_data = []
        for data_file in data_files:
            loader = create_loader(data_file)
            data = list(loader.load())
            all_data.extend(data)
        
        self.logger.info(f"Loaded {len(all_data)} items from Gemini files")
        
        # Sample with balanced phonetized/non-phonetized ratio
        balanced_data = self.sampler.sample_phonetized_dialogue(all_data, sample_size, phonetized_ratio)
        
        self.logger.info(f"Balanced sample contains {len(balanced_data)} items")
        
        return balanced_data
    
    def balance_mixed_data(self, gb_file: Path, gemini_files: List[Path], 
                          sample_size: int, dialogue_ratio: float = 0.5) -> Tuple[List[Any], List[Any]]:
        """Balance mixed data sources."""
        self.logger.info("Balancing mixed data sources")
        
        # Load GB data (non-dialogue)
        gb_loader = create_loader(gb_file)
        gb_data = list(gb_loader.load())
        
        # Load Gemini data (dialogue)
        gemini_data = []
        for gemini_file in gemini_files:
            loader = create_loader(gemini_file)
            data = list(loader.load())
            gemini_data.extend(data)
        
        self.logger.info(f"Loaded {len(gb_data)} GB items and {len(gemini_data)} Gemini items")
        
        # Calculate sample sizes
        dialogue_sample_size = int(sample_size * dialogue_ratio)
        non_dialogue_sample_size = sample_size - dialogue_sample_size
        
        # Sample from each source
        sampled_gb = self.sampler.sample(gb_data, non_dialogue_sample_size, 0.0)  # 0% dialogue for GB
        sampled_gemini = self.sampler.sample(gemini_data, dialogue_sample_size, 1.0)  # 100% dialogue for Gemini
        
        self.logger.info(f"Sampled {len(sampled_gb)} GB items and {len(sampled_gemini)} Gemini items")
        
        return sampled_gb, sampled_gemini
    
    def save_balanced_data(self, data: List[Any], output_file: Path) -> None:
        """Save balanced data to file."""
        self.logger.info(f"Saving {len(data)} balanced items to {output_file}")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for item in data:
                    # Convert to Prodigy format with proper meta fields
                    prodigy_item = self._convert_to_prodigy_format(item)
                    
                    import json
                    f.write(json.dumps(prodigy_item, ensure_ascii=False) + "\n")
            
            self.logger.info(f"Successfully saved balanced data to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save balanced data to {output_file}: {e}")
            raise
    
    def _convert_to_prodigy_format(self, item: Any) -> Dict[str, Any]:
        """Convert data item to Prodigy format with proper meta fields."""
        from src.data.loaders import GBDataItem, GeminiDataItem
        
        if isinstance(item, GBDataItem):
            # Use the formatter for GB data
            is_dialogue = self.sampler._is_dialogue_sample(item)
            return self.formatter.format_gb_data(item, is_dialogue=is_dialogue)
        
        elif isinstance(item, GeminiDataItem):
            # Use the formatter for Gemini data
            is_phonetized = self.sampler._is_phonetized_sample(item)
            return self.formatter.format_gemini_data(item, is_phonetized=is_phonetized)
        
        else:
            # Fallback for unknown types
            return {
                "text": str(item),
                "meta": {
                    "source": "unknown",
                    "is_dialogue": False
                }
            }
    
    def get_balance_statistics(self, data: List[Any]) -> Dict[str, int]:
        """Get statistics about data balance."""
        phonetized_count = 0
        non_phonetized_count = 0
        
        for item in data:
            if self.sampler._is_phonetized_sample(item):
                phonetized_count += 1
            else:
                non_phonetized_count += 1
        
        total = len(data)
        phonetized_ratio = phonetized_count / total if total > 0 else 0
        
        return {
            "total": total,
            "phonetized": phonetized_count,
            "non_phonetized": non_phonetized_count,
            "phonetized_ratio": phonetized_ratio,
            "non_phonetized_ratio": 1 - phonetized_ratio
        }
