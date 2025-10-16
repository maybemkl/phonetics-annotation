#!/usr/bin/env python3
"""Run Prodigy localhost annotation interface."""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prodigy import ProdigyRunner, ProdigyFormatter
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def main():
    """Main entry point for Prodigy localhost annotation."""
    parser = argparse.ArgumentParser(
        description="Run Prodigy localhost annotation interface"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input data file (JSONL format)"
    )
    parser.add_argument(
        "--patterns-file",
        type=Path,
        help="Patterns file for Prodigy (JSONL format)"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="phonetics_anno",
        help="Prodigy database name (default: phonetics_anno)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="en_core_web_sm",
        help="SpaCy model to use (default: en_core_web_sm)"
    )
    parser.add_argument(
        "--labels",
        type=str,
        nargs="+",
        default=["PHONETIC", "DIALECT", "SLANG"],
        help="Annotation labels (default: PHONETIC DIALECT SLANG)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to run Prodigy on (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run Prodigy on (default: 8080)"
    )
    parser.add_argument(
        "--annotation-type",
        choices=["spans", "ner"],
        default="spans",
        help="Type of annotation (default: spans)"
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
        # Validate input file
        if not args.input_file.exists():
            logger.error(f"Input file not found: {args.input_file}")
            return 1
        
        # Validate patterns file if provided
        if args.patterns_file and not args.patterns_file.exists():
            logger.error(f"Patterns file not found: {args.patterns_file}")
            return 1
        
        logger.info(f"Starting Prodigy {args.annotation_type} annotation")
        logger.info(f"Database: {args.db_name}")
        logger.info(f"Model: {args.model}")
        logger.info(f"Labels: {args.labels}")
        logger.info(f"Host: {args.host}:{args.port}")
        
        # Initialize Prodigy runner
        runner = ProdigyRunner()
        
        # Check Prodigy installation
        if not runner.check_prodigy_installation():
            logger.error("Prodigy is not properly installed or not in PATH")
            return 1
        
        # Run Prodigy command based on annotation type
        if args.annotation_type == "spans":
            process = runner.run_spans_manual(
                db_name=args.db_name,
                model=args.model,
                input_file=args.input_file,
                patterns_file=args.patterns_file,
                labels=args.labels,
                host=args.host,
                port=args.port
            )
        elif args.annotation_type == "ner":
            process = runner.run_ner_manual(
                db_name=args.db_name,
                model=args.model,
                input_file=args.input_file,
                patterns_file=args.patterns_file,
                labels=args.labels,
                host=args.host,
                port=args.port
            )
        else:
            logger.error(f"Unknown annotation type: {args.annotation_type}")
            return 1
        
        logger.info(f"Prodigy started successfully!")
        logger.info(f"Open your browser and go to: http://{args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop the annotation session")
        
        try:
            # Wait for the process to complete
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping Prodigy annotation session...")
            process.terminate()
            process.wait()
            logger.info("Annotation session stopped")
        
        # Get final statistics
        stats = runner.get_annotation_stats(args.db_name)
        if stats:
            logger.info(f"Annotation statistics: {stats}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Prodigy annotation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
