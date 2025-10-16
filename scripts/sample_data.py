#!/usr/bin/env python3
"""Sample data with balanced dialogue/non-dialogue splits."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sampling import DataBalancer
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    """Main entry point for data sampling."""
    parser = argparse.ArgumentParser(
        description="Sample data with balanced dialogue/non-dialogue splits"
    )
    parser.add_argument(
        "--gb-file",
        type=Path,
        help="GB data file (non-dialogue source)"
    )
    parser.add_argument(
        "--gemini-files",
        type=Path,
        nargs="+",
        help="Gemini data files (dialogue source)"
    )
    parser.add_argument(
        "--gemini-dir",
        type=Path,
        help="Directory containing Gemini data files (dialogue source)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file for sampled data"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=1000,
        help="Total sample size (default: 1000)"
    )
    parser.add_argument(
        "--phonetized-ratio",
        type=float,
        default=0.5,
        help="Ratio of phonetized dialogue samples (default: 0.5)"
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
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
    
    try:
        # Validate arguments
        if not args.gb_file and not args.gemini_files and not args.gemini_dir:
            logger.error("Must provide either --gb-file, --gemini-files, or --gemini-dir")
            return 1
        
        if args.gb_file and not args.gb_file.exists():
            logger.error(f"GB file not found: {args.gb_file}")
            return 1
        
        if args.gemini_files:
            for gemini_file in args.gemini_files:
                if not gemini_file.exists():
                    logger.error(f"Gemini file not found: {gemini_file}")
                    return 1
        
        if args.gemini_dir and not args.gemini_dir.exists():
            logger.error(f"Gemini directory not found: {args.gemini_dir}")
            return 1
        
        logger.info(f"Starting data sampling with {args.sample_size} samples")
        logger.info(f"Phonetized ratio: {args.phonetized_ratio}")
        logger.info(f"Random seed: {args.random_seed}")
        
        # Initialize balancer with patterns file
        patterns_file = Path("patterns.jsonl")
        balancer = DataBalancer(random_seed=args.random_seed, patterns_file=patterns_file)
        
        # Get Gemini files from directory if specified
        gemini_files = args.gemini_files
        if args.gemini_dir:
            gemini_files = list(args.gemini_dir.glob("*.jsonl"))
            logger.info(f"Found {len(gemini_files)} Gemini files in {args.gemini_dir}")
        
        # Sample data based on available sources
        if args.gb_file and gemini_files:
            # Mixed data sources
            logger.info("Using mixed data sources (GB + Gemini)")
            gb_data, gemini_data = balancer.balance_mixed_data(
                gb_file=args.gb_file,
                gemini_files=gemini_files,
                sample_size=args.sample_size,
                dialogue_ratio=args.phonetized_ratio
            )
            
            # Combine data
            balanced_data = gb_data + gemini_data
            
        elif args.gb_file:
            # GB data only
            logger.info("Using GB data only")
            balanced_data = balancer.balance_gb_data(
                data_file=args.gb_file,
                sample_size=args.sample_size,
                dialogue_ratio=args.phonetized_ratio
            )
            
        else:
            # Gemini data only
            logger.info("Using Gemini data only")
            balanced_data = balancer.balance_gemini_data(
                data_files=gemini_files,
                sample_size=args.sample_size,
                phonetized_ratio=args.phonetized_ratio
            )
        
        # Get balance statistics
        stats = balancer.get_balance_statistics(balanced_data)
        logger.info(f"Balance statistics: {stats}")
        
        # Generate timestamped output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = args.output.parent / f"{args.output.stem}_{timestamp}{args.output.suffix}"
        
        # Save balanced data
        balancer.save_balanced_data(balanced_data, output_path)
        
        logger.info(f"Successfully sampled {len(balanced_data)} items")
        logger.info(f"Sampled data saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Data sampling failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
