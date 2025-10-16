# Phonetics Annotation Pipeline

A robust pipeline for filtering dialogue extracts for phoneticized text, sampling from extracts with and without dialogue (50/50 split), and using those samples as input for annotation in Prodigy.

## Overview

This project processes phonetic data from American literature, generates patterns for Prodigy annotation, and manages the complete annotation workflow. The architecture follows best practices for maintainability, testability, and scalability.

## Features

- **Data Processing**: Load and validate data from multiple sources (GB data, Gemini outputs)
- **Pattern Generation**: Extract phonetic patterns with configurable filtering
- **Balanced Sampling**: Create 50/50 splits between dialogue and non-dialogue samples
- **Prodigy Integration**: Format data for Prodigy annotation interface
- **Configuration Management**: Environment-based configuration with validation
- **Comprehensive Logging**: Structured logging with multiple output formats
- **Testing**: Full test coverage with pytest
- **Documentation**: Comprehensive documentation and examples

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd phonetics-annotation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment configuration:
```bash
cp env.example .env
# Edit .env with your specific settings
```

### Basic Usage

1. **Generate patterns from GB data**:
```bash
python scripts/generate_patterns.py GB_0_3.jsonl -o patterns.jsonl
```

2. **Run Prodigy annotation**:
```bash
# Local development
python run_prodigy.py

# AWS deployment
python run_prodigy.py --mode aws
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Modules

- **`config/`**: Configuration management with Pydantic validation
- **`src/data/`**: Data loading, validation, and processing
- **`src/patterns/`**: Pattern generation and filtering
- **`src/sampling/`**: Balanced sampling strategies
- **`src/prodigy/`**: Prodigy integration and formatting
- **`src/utils/`**: Common utilities and logging

### Key Benefits

- **Maintainable**: Clear structure and separation of concerns
- **Testable**: Comprehensive test coverage
- **Configurable**: Environment-based configuration
- **Robust**: Error handling and validation
- **Documented**: Self-documenting code and comprehensive docs

## Configuration

The project uses both environment-based configuration and YAML configuration files.

### Environment Configuration
Copy `env.example` to `.env` and customize:

```bash
# Data paths
DATA_ROOT=./data
RAW_DATA_PATH=./data/raw

# Pattern generation
MIN_PATTERN_LENGTH=3
ENABLE_STOPWORD_FILTER=true

# Sampling
DIALOGUE_RATIO=0.5
SAMPLE_SIZE=1000
```

### Prodigy Configuration
Prodigy settings are configured in `prodigy_config.yaml`:

```yaml
prodigy:
  port: 8081
  command: spans.manual
  dataset: phonetics_anno
  model: en_core_web_sm
  data_file: data/processed/samples/balanced_sample_20251016_140158.jsonl
  loader: jsonl
  labels: PHONETIC,NOT_DIALOGUE,ERROR
  patterns_file: patterns.jsonl
```

You can use different config files:
```bash
python run_prodigy.py my_custom_config.yaml --mode local
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/ scripts/
isort src/ tests/ scripts/
```

### Type Checking

```bash
mypy src/
```

## Data Flow

1. **Data Ingestion**: Load raw data from various sources
2. **Validation**: Validate data integrity and format
3. **Pattern Generation**: Extract phonetic patterns from validated data
4. **Sampling**: Create balanced samples (50/50 dialogue/non-dialogue)
5. **Prodigy Formatting**: Convert samples to Prodigy format
6. **Annotation**: Run Prodigy annotation interface
7. **Output**: Export annotated results

## AWS Deployment

### Instance Recommendations
- **t4g.small** (2 vCPU, 2GB RAM) - ~$12/month, perfect for Prodigy
- **t4g.micro** (2 vCPU, 1GB RAM) - ~$6/month, good for light workloads

### Security Group Configuration
Allow these ports:
- SSH (22) from your IP
- HTTP (80) from anywhere  
- Custom TCP (8080) from anywhere

### Cost Optimization
- Use Spot Instances for development
- Stop instances when not in use
- Set up auto-shutdown for non-production hours

### Monitoring
```bash
# Health check
curl -f http://localhost:8080/health || echo "Prodigy down"

# Memory usage
free -h
htop
```

### Troubleshooting
```bash
# Port issues
sudo netstat -tlnp | grep 8080

# Permission issues  
sudo chown -R ubuntu:ubuntu /home/ubuntu/phonetics-annotation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[Add your license information here]
