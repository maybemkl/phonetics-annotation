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
    
    # Set host if specified
    if 'host' in config:
        env['PRODIGY_HOST'] = config['host']
    
    # Set CORS if specified
    if 'cors' in config and config['cors']:
        env['PRODIGY_CORS'] = 'true'
    
    # Set validation if specified
    if 'validate' in config and config['validate']:
        env['PRODIGY_VALIDATE'] = 'true'
    
    # Set database settings if specified
    if 'db' in config:
        env['PRODIGY_DB'] = config['db']
    if 'db_settings' in config and config['db_settings']:
        # Convert db_settings dict to environment variables
        for key, value in config['db_settings'].items():
            env[f'PRODIGY_DB_{key.upper()}'] = str(value)
    
    # Set logging if specified
    if 'PRODIGY_LOGGING' in config:
        env['PRODIGY_LOGGING'] = config['PRODIGY_LOGGING']
    
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
    
    # Add optional arguments if they exist (only valid for spans.manual)
    if 'highlight_chars' in config and config['highlight_chars']:
        cmd.append('--highlight-chars')
    if 'edit_text' in config and config['edit_text']:
        cmd.append('--edit-text')
    if 'use_annotations' in config and config['use_annotations']:
        cmd.append('--use-annotations')
    
    print(f"Running: {' '.join(cmd)}")
    print(f"Host: {config.get('host', 'localhost (default)')}")
    print(f"Port: {config['port']}")
    print(f"Data file: {config['data_file']}")
    print(f"Labels: {config['labels']}")
    print(f"CORS: {config.get('cors', False)}")
    print(f"Validation: {config.get('validate', False)}")
    
    if config.get('host') == '0.0.0.0':
        print("⚠️  Warning: Host set to 0.0.0.0 - Prodigy will be accessible from external networks")
    else:
        print("ℹ️  Prodigy will be accessible at http://localhost:{}".format(config['port']))
    
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
