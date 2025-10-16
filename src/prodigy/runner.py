"""Prodigy execution utilities."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProdigyRunner:
    """Run Prodigy commands programmatically."""
    
    def __init__(self, prodigy_path: Optional[str] = None):
        """Initialize Prodigy runner."""
        self.prodigy_path = prodigy_path or "prodigy"
        self.logger = get_logger(self.__class__.__name__)
    
    def run_spans_manual(self, 
                        db_name: str,
                        model: str,
                        input_file: Path,
                        patterns_file: Optional[Path] = None,
                        labels: List[str] = None,
                        host: str = "localhost",
                        port: int = 8080,
                        **kwargs) -> subprocess.Popen:
        """Run Prodigy spans.manual command."""
        
        if labels is None:
            labels = ["PHONETIC", "DIALECT", "SLANG"]
        
        # Build command
        cmd = [
            self.prodigy_path,
            "spans.manual",
            db_name,
            model,
            str(input_file),
            "--loader", "jsonl",
            "--label", ",".join(labels),
            "--host", host,
            "--port", str(port)
        ]
        
        # Add patterns file if provided
        if patterns_file and patterns_file.exists():
            cmd.extend(["--patterns", str(patterns_file)])
        
        # Add additional arguments
        for key, value in kwargs.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
        
        self.logger.info(f"Running Prodigy command: {' '.join(cmd)}")
        
        try:
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to run Prodigy command: {e}")
            raise
    
    def run_ner_manual(self,
                      db_name: str,
                      model: str,
                      input_file: Path,
                      patterns_file: Optional[Path] = None,
                      labels: List[str] = None,
                      host: str = "localhost",
                      port: int = 8080,
                      **kwargs) -> subprocess.Popen:
        """Run Prodigy ner.manual command."""
        
        if labels is None:
            labels = ["PHONETIC", "DIALECT", "SLANG"]
        
        # Build command
        cmd = [
            self.prodigy_path,
            "ner.manual",
            db_name,
            model,
            str(input_file),
            "--loader", "jsonl",
            "--label", ",".join(labels),
            "--host", host,
            "--port", str(port)
        ]
        
        # Add patterns file if provided
        if patterns_file and patterns_file.exists():
            cmd.extend(["--patterns", str(patterns_file)])
        
        # Add additional arguments
        for key, value in kwargs.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
        
        self.logger.info(f"Running Prodigy command: {' '.join(cmd)}")
        
        try:
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to run Prodigy command: {e}")
            raise
    
    def check_prodigy_installation(self) -> bool:
        """Check if Prodigy is properly installed."""
        try:
            result = subprocess.run(
                [self.prodigy_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Prodigy version: {result.stdout.strip()}")
                return True
            else:
                self.logger.error(f"Prodigy check failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check Prodigy installation: {e}")
            return False
    
    def get_annotation_stats(self, db_name: str) -> Dict[str, Any]:
        """Get annotation statistics from Prodigy database."""
        try:
            result = subprocess.run(
                [self.prodigy_path, "db-stats", db_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse the output (this is a simplified version)
                stats = {
                    "total_examples": 0,
                    "annotated_examples": 0,
                    "pending_examples": 0
                }
                
                # Parse the output to extract statistics
                for line in result.stdout.split('\n'):
                    if 'total' in line.lower():
                        try:
                            stats["total_examples"] = int(line.split()[-1])
                        except (ValueError, IndexError):
                            pass
                    elif 'annotated' in line.lower():
                        try:
                            stats["annotated_examples"] = int(line.split()[-1])
                        except (ValueError, IndexError):
                            pass
                
                stats["pending_examples"] = stats["total_examples"] - stats["annotated_examples"]
                
                return stats
            else:
                self.logger.error(f"Failed to get stats: {result.stderr}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to get annotation stats: {e}")
            return {}
