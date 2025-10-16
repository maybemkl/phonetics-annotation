#!/usr/bin/env python3
"""Run the complete phonetics annotation workflow."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.patterns import PatternGenerator, PatternFilter
from src.sampling import DataBalancer
from src.prodigy import ProdigyRunner
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    """Main entry point for the complete workflow."""
    parser = argparse.ArgumentParser(
        description="Run the complete phonetics annotation workflow"
    )
    
    # Data sources
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
    
    # Pattern generation
    parser.add_argument(
        "--generate-patterns",
        action="store_true",
        help="Generate patterns from GB data"
    )
    parser.add_argument(
        "--patterns-output",
        type=Path,
        default=Path("data/processed/patterns/patterns.jsonl"),
        help="Output file for patterns"
    )
    
    # Sampling
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Sample balanced data"
    )
    parser.add_argument(
        "--sample-output",
        type=Path,
        default=Path("data/processed/samples/balanced_sample.jsonl"),
        help="Output file for sampled data"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=1000,
        help="Total sample size (default: 1000)"
    )
    parser.add_argument(
        "--dialogue-ratio",
        type=float,
        default=0.5,
        help="Ratio of dialogue samples (default: 0.5)"
    )
    
    # Prodigy annotation
    parser.add_argument(
        "--run-prodigy",
        action="store_true",
        help="Run Prodigy annotation interface"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="phonetics_anno",
        help="Prodigy database name"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="en_core_web_sm",
        help="SpaCy model to use"
    )
    parser.add_argument(
        "--labels",
        type=str,
        nargs="+",
        default=["PHONETIC", "DIALECT", "SLANG"],
        help="Annotation labels"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Prodigy host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Prodigy port"
    )
    
    # General options
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
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
        logger.info("Starting phonetics annotation workflow")
        
        # Step 1: Generate patterns
        if args.generate_patterns:
            if not args.gb_file or not args.gb_file.exists():
                logger.error("GB file required for pattern generation")
                return 1
            
            logger.info("Step 1: Generating patterns from GB data")
            generator = PatternGenerator()
            patterns = generator.generate_from_gb_data(args.gb_file)
            
            # Apply filtering
            filter_obj = PatternFilter()
            patterns = filter_obj.deduplicate_patterns(patterns)
            
            # Save patterns
            generator.save_patterns(patterns, args.patterns_output)
            logger.info(f"Generated {len(patterns)} patterns")
        
        # Step 2: Sample data
        if args.sample_data:
            if not args.gb_file and not args.gemini_files and not args.gemini_dir:
                logger.error("Must provide either --gb-file, --gemini-files, or --gemini-dir for sampling")
                return 1
            
            logger.info("Step 2: Sampling balanced data")
            balancer = DataBalancer(random_seed=args.random_seed)
            
            # Get Gemini files from directory if specified
            gemini_files = args.gemini_files
            if args.gemini_dir:
                gemini_files = list(args.gemini_dir.glob("*.jsonl"))
                logger.info(f"Found {len(gemini_files)} Gemini files in {args.gemini_dir}")
            
            if args.gb_file and gemini_files:
                # Mixed data sources
                gb_data, gemini_data = balancer.balance_mixed_data(
                    gb_file=args.gb_file,
                    gemini_files=gemini_files,
                    sample_size=args.sample_size,
                    dialogue_ratio=args.dialogue_ratio
                )
                balanced_data = gb_data + gemini_data
            elif args.gb_file:
                # GB data only
                balanced_data = balancer.balance_gb_data(
                    data_file=args.gb_file,
                    sample_size=args.sample_size,
                    dialogue_ratio=args.dialogue_ratio
                )
            else:
                # Gemini data only
                balanced_data = balancer.balance_gemini_data(
                    data_files=gemini_files,
                    sample_size=args.sample_size,
                    dialogue_ratio=args.dialogue_ratio
                )
            
            # Save balanced data
            balancer.save_balanced_data(balanced_data, args.sample_output)
            
            # Get statistics
            stats = balancer.get_balance_statistics(balanced_data)
            logger.info(f"Sampled {len(balanced_data)} items with balance: {stats}")
        
        # Step 3: Run Prodigy annotation
        if args.run_prodigy:
            if not args.sample_output.exists():
                logger.error(f"Sample data file not found: {args.sample_output}")
                return 1
            
            logger.info("Step 3: Running Prodigy annotation interface")
            runner = ProdigyRunner()
            
            # Check Prodigy installation
            if not runner.check_prodigy_installation():
                logger.error("Prodigy is not properly installed or not in PATH")
                return 1
            
            # Run Prodigy
            process = runner.run_spans_manual(
                db_name=args.db_name,
                model=args.model,
                input_file=args.sample_output,
                patterns_file=args.patterns_output if args.patterns_output.exists() else None,
                labels=args.labels,
                host=args.host,
                port=args.port
            )
            
            logger.info(f"Prodigy started successfully!")
            logger.info(f"Open your browser and go to: http://{args.host}:{args.port}")
            logger.info("Press Ctrl+C to stop the annotation session")
            
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("Stopping Prodigy annotation session...")
                process.terminate()
                process.wait()
                logger.info("Annotation session stopped")
            
            # Get final statistics
            stats = runner.get_annotation_stats(args.db_name)
            if stats:
                logger.info(f"Final annotation statistics: {stats}")
        
        logger.info("Workflow completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
