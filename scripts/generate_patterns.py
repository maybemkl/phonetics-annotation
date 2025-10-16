#!/usr/bin/env python3
"""Generate patterns from phonetic data using the new architecture."""

import argparse
from pathlib import Path
from typing import Optional

from src.patterns import PatternGenerator
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
        
        # Generate patterns
        generator = PatternGenerator()
        patterns = generator.generate_from_gb_data(args.input_file)
        
        # Save patterns
        generator.save_patterns(patterns, output_file)
        
        logger.info(f"Successfully generated {len(patterns)} patterns")
        return 0
        
    except Exception as e:
        logger.error(f"Pattern generation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
