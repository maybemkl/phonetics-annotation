#!/usr/bin/env python3
"""Generate patterns from phonetic data using the new architecture."""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.patterns.generator import PatternGenerator
from src.patterns.filters import PatternFilter
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    """Main entry point for pattern generation."""
    parser = argparse.ArgumentParser(
        description="Generate patterns from phonetic data for Prodigy annotation"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input GB data file (JSONL format)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output patterns file (default: patterns.jsonl)"
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=3,
        help="Minimum pattern length (default: 3)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=50,
        help="Maximum pattern length (default: 50)"
    )
    parser.add_argument(
        "--no-stopword-filter",
        action="store_true",
        help="Disable stopword filtering"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--log-format",
        choices=["json", "text"],
        default="text",
        help="Log format"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_format=args.log_format
    )
    
    # Determine output file
    output_file = args.output or Path("patterns.jsonl")
    
    try:
        # Validate input file
        if not args.input_file.exists():
            logger.error(f"Input file not found: {args.input_file}")
            return 1
        
        logger.info(f"Starting pattern generation from {args.input_file}")
        logger.info(f"Min length: {args.min_length}, Max length: {args.max_length}")
        logger.info(f"Stopword filter: {not args.no_stopword_filter}")
        
        # Generate patterns
        generator = PatternGenerator()
        patterns = generator.generate_from_gb_data(args.input_file)
        
        # Apply additional filtering if needed
        if args.min_length != 3 or args.max_length != 50:
            logger.info("Applying custom length filtering...")
            filter_obj = PatternFilter()
            patterns = filter_obj.filter_patterns(patterns, min_length=args.min_length)
        
        # Deduplicate patterns
        logger.info("Deduplicating patterns...")
        filter_obj = PatternFilter()
        patterns = filter_obj.deduplicate_patterns(patterns)
        
        # Save patterns
        generator.save_patterns(patterns, output_file)
        
        logger.info(f"Successfully generated {len(patterns)} patterns")
        logger.info(f"Patterns saved to: {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Pattern generation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
