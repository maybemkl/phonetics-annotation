#!/usr/bin/env python3
"""Run Prodigy with configuration from YAML file."""

import os
import subprocess
import sys
import yaml
from pathlib import Path

def load_config(config_file="prodigy_config.yaml"):
    """Load configuration from YAML file."""
    if not Path(config_file).exists():
        print(f"Error: Configuration file {config_file} not found!")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config['prodigy']

def run_prodigy(config):
    """Run Prodigy with the given configuration."""
    # Set environment variables
    env = os.environ.copy()
    env['PRODIGY_PORT'] = str(config['port'])
    
    # Build command
    cmd = [
        'prodigy',
        config['command'],
        config['dataset'],
        config['model'],
        config['data_file'],
        '--loader', config['loader'],
        '--label', config['labels'],
        '--patterns', config['patterns_file']
    ]
    
    # Add optional arguments if they exist
    if 'batch_size' in config:
        cmd.extend(['--batch-size', str(config['batch_size'])])
    if 'show_instructions' in config and config['show_instructions']:
        cmd.append('--show-instructions')
    if 'auto_save' in config and config['auto_save']:
        cmd.append('--auto-save')
    
    print(f"Running: {' '.join(cmd)}")
    print(f"Port: {config['port']}")
    print(f"Data file: {config['data_file']}")
    print(f"Labels: {config['labels']}")
    
    # Run Prodigy
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Prodigy failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nProdigy stopped by user")
        sys.exit(0)

def main():
    """Main entry point."""
    config_file = sys.argv[1] if len(sys.argv) > 1 else "prodigy_config.yaml"
    config = load_config(config_file)
    run_prodigy(config)

if __name__ == "__main__":
    main()
