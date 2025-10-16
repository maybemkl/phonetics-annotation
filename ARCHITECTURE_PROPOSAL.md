# Phonetics Annotation Pipeline - Architecture Proposal

## Overview
This document outlines a proposed architecture for the phonetics annotation pipeline that processes dialogue extracts, creates patterns for Prodigy annotation, and manages data flow between different stages.

## Current Issues
- Flat directory structure with poor organization
- Hardcoded paths and no configuration management
- Lack of error handling and data validation
- No logging or testing infrastructure
- Mixed responsibilities in scripts
- No dependency management

## Proposed Directory Structure

```
phonetics-annotation/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── 
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── prodigy_config.yaml
├── 
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py          # Data loading utilities
│   │   ├── validators.py       # Data validation
│   │   └── processors.py       # Data processing logic
│   ├── patterns/
│   │   ├── __init__.py
│   │   ├── generator.py        # Pattern generation logic
│   │   └── filters.py          # Pattern filtering
│   ├── sampling/
│   │   ├── __init__.py
│   │   ├── strategies.py       # Sampling strategies
│   │   └── balancer.py         # 50/50 split logic
│   ├── prodigy/
│   │   ├── __init__.py
│   │   ├── formatter.py        # Prodigy data formatting
│   │   └── runner.py           # Prodigy execution
│   └── utils/
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       └── helpers.py          # Common utilities
├── 
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data/
│   ├── test_loaders.py
│   ├── test_patterns.py
│   ├── test_sampling.py
│   └── test_prodigy.py
├── 
├── scripts/
│   ├── generate_patterns.py
│   ├── sample_data.py
│   ├── format_for_prodigy.py
│   └── run_annotation.py
├── 
├── data/
│   ├── raw/                    # Original data files
│   │   ├── gb_data/
│   │   └── gemini_outputs/
│   ├── processed/              # Processed data
│   │   ├── patterns/
│   │   ├── samples/
│   │   └── prodigy_ready/
│   └── outputs/                # Final outputs
│       └── annotations/
├── 
├── logs/                       # Log files
├── 
└── docs/
    ├── setup.md
    ├── usage.md
    └── api.md
```

## Key Components

### 1. Configuration Management (`config/`)
- **settings.py**: Centralized configuration using Pydantic
- **prodigy_config.yaml**: Prodigy-specific settings
- Environment-based configuration with `.env` files

### 2. Data Layer (`src/data/`)
- **loaders.py**: Unified data loading with support for multiple formats
- **validators.py**: Data integrity checks and validation
- **processors.py**: Data transformation and cleaning logic

### 3. Pattern Generation (`src/patterns/`)
- **generator.py**: Pattern creation from phonetic data
- **filters.py**: Stopword filtering and pattern deduplication

### 4. Sampling Module (`src/sampling/`)
- **strategies.py**: Different sampling strategies (random, stratified, etc.)
- **balancer.py**: 50/50 split logic for dialogue/non-dialogue samples

### 5. Prodigy Integration (`src/prodigy/`)
- **formatter.py**: Convert data to Prodigy format
- **runner.py**: Execute Prodigy commands programmatically

### 6. Testing (`tests/`)
- Comprehensive test coverage
- Fixtures for test data
- Integration tests for full pipeline

### 7. Scripts (`scripts/`)
- Command-line interfaces for each major operation
- Clear entry points for different workflows

## Best Practices Implemented

### 1. **Separation of Concerns**
- Each module has a single responsibility
- Clear interfaces between components
- Dependency injection for testability

### 2. **Configuration Management**
- Environment-based configuration
- Type-safe settings with Pydantic
- No hardcoded paths or values

### 3. **Error Handling & Logging**
- Comprehensive error handling
- Structured logging with different levels
- Graceful failure modes

### 4. **Data Validation**
- Input validation at data boundaries
- Type checking with Pydantic models
- Data integrity checks

### 5. **Testing**
- Unit tests for all components
- Integration tests for workflows
- Test data fixtures

### 6. **Documentation**
- Comprehensive docstrings
- API documentation
- Usage examples

### 7. **Dependency Management**
- `requirements.txt` for pip
- `pyproject.toml` for modern Python packaging
- Docker support for reproducible environments

## Data Flow

1. **Data Ingestion**: Load raw data from various sources
2. **Validation**: Validate data integrity and format
3. **Pattern Generation**: Extract phonetic patterns from validated data
4. **Sampling**: Create balanced samples (50/50 dialogue/non-dialogue)
5. **Prodigy Formatting**: Convert samples to Prodigy format
6. **Annotation**: Run Prodigy annotation interface
7. **Output**: Export annotated results

## Benefits

- **Maintainability**: Clear structure and separation of concerns
- **Testability**: Comprehensive test coverage
- **Scalability**: Modular design allows easy extension
- **Reliability**: Error handling and validation
- **Documentation**: Self-documenting code and comprehensive docs
- **Reproducibility**: Docker and dependency management
- **Flexibility**: Configurable and extensible design

## Migration Strategy

1. Create new directory structure
2. Refactor existing scripts into new modules
3. Add configuration management
4. Implement error handling and logging
5. Add comprehensive tests
6. Update documentation
7. Migrate data to new structure
8. Validate functionality

This architecture provides a solid foundation for a production-ready phonetics annotation pipeline while maintaining the simplicity needed for research workflows.
