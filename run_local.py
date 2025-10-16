#!/usr/bin/env python3
"""Run Prodigy locally with localhost configuration."""

import os
import subprocess
import sys
import yaml
from pathlib import Path

def run_prodigy_local():
    """Run Prodigy with localhost configuration."""
    # Set environment variables for local development
    env = os.environ.copy()
    env['PRODIGY_PORT'] = '8081'
    env['PRODIGY_HOST'] = 'localhost'  # Explicitly set to localhost
    
    # Build command for local development
    cmd = [
        'prodigy',
        'spans.manual',
        'phonetics_anno',
        'en_core_web_sm',
        'data/processed/samples/balanced_sample_20251016_153416.jsonl',
        '--loader', 'jsonl',
        '--label', 'PHONETIC,NOT_DIALOGUE,ERROR',
        '--patterns', 'patterns.jsonl',
        '--batch-size', '10',
        '--show-instructions',
        '--auto-save'
    ]
    
    print("🚀 Starting Prodigy locally...")
    print(f"Running: {' '.join(cmd)}")
    print("ℹ️  Prodigy will be accessible at http://localhost:8081")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Run Prodigy
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Prodigy failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Prodigy stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    run_prodigy_local()
