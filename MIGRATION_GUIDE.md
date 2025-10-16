# Migration Guide: From Current to New Architecture

This guide helps you transition from the current flat structure to the new modular architecture.

## Current vs New Structure

### Current Structure
```
phonetics-annotation/
├── py/
│   ├── format_jsonl_for_prodigy.py
│   └── make_patterns.py
├── input/
│   ├── gemini_outputs/
│   └── prodigy/
├── patterns.jsonl
├── GB_0_3.jsonl
└── prodigy_localhost.sh
```

### New Structure
```
phonetics-annotation/
├── config/           # Configuration management
├── src/              # Source code modules
├── scripts/          # Command-line scripts
├── tests/            # Test suite
├── data/             # Organized data directories
├── logs/             # Log files
└── docs/             # Documentation
```

## Migration Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Configuration

```bash
cp env.example .env
# Edit .env with your specific settings
```

### 3. Migrate Data

Move your existing data to the new structure:

```bash
# Create new data directories
mkdir -p data/raw/gb_data
mkdir -p data/raw/gemini_outputs
mkdir -p data/processed/patterns
mkdir -p data/processed/samples
mkdir -p data/outputs/annotations

# Move existing data
mv GB_0_3.jsonl data/raw/gb_data/
mv input/gemini_outputs/* data/raw/gemini_outputs/
mv patterns.jsonl data/processed/patterns/
```

### 4. Update Scripts

Replace old script usage with new commands:

#### Old Pattern Generation
```bash
python py/make_patterns.py
```

#### New Pattern Generation
```bash
python scripts/generate_patterns.py data/raw/gb_data/GB_0_3.jsonl -o data/processed/patterns/patterns.jsonl
```

#### Old Prodigy Formatting
```bash
python py/format_jsonl_for_prodigy.py
```

#### New Prodigy Formatting
```bash
python scripts/format_prodigy.py data/raw/gemini_outputs/ -o data/processed/prodigy_ready/
```

### 5. Update Prodigy Command

Update your Prodigy command to use the new data paths:

```bash
# Old
prodigy spans.manual phonetics_anno en_core_web_sm input/prodigy/WC27513_dialogue.jsonl \
  --loader jsonl \
  --label PHONETIC,DIALECT,SLANG \
  --patterns patterns.jsonl

# New
prodigy spans.manual phonetics_anno en_core_web_sm data/processed/prodigy_ready/WC27513_dialogue.jsonl \
  --loader jsonl \
  --label PHONETIC,DIALECT,SLANG \
  --patterns data/processed/patterns/patterns.jsonl
```

## Key Improvements

### 1. Configuration Management
- **Before**: Hardcoded paths and settings
- **After**: Environment-based configuration with validation

### 2. Error Handling
- **Before**: Basic error handling
- **After**: Comprehensive error handling with logging

### 3. Data Validation
- **Before**: No data validation
- **After**: Pydantic models with validation

### 4. Logging
- **Before**: Print statements
- **After**: Structured logging with multiple levels

### 5. Testing
- **Before**: No tests
- **After**: Comprehensive test suite

### 6. Code Organization
- **Before**: Monolithic scripts
- **After**: Modular, reusable components

## Backward Compatibility

The new architecture maintains backward compatibility for basic functionality:

1. **Pattern Generation**: Same input/output format
2. **Prodigy Formatting**: Same output format
3. **Data Processing**: Same data structures

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root
2. **Configuration Errors**: Check your `.env` file
3. **Data Path Errors**: Verify data files are in the correct locations

### Getting Help

1. Check the logs in `logs/phonetics_annotation.log`
2. Run with `--log-level DEBUG` for detailed output
3. Check the test suite: `pytest tests/`

## Next Steps

After migration:

1. **Run Tests**: `pytest` to ensure everything works
2. **Update Documentation**: Customize README.md for your specific use case
3. **Add Features**: Use the modular structure to add new functionality
4. **Monitor Logs**: Use structured logging for better debugging

## Rollback Plan

If you need to rollback:

1. Keep a backup of your original `py/` directory
2. The new structure doesn't modify existing data files
3. You can always run the old scripts if needed

The new architecture is designed to be a drop-in replacement with significant improvements in maintainability and reliability.
