"""Configuration settings for the phonetics annotation pipeline."""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Data-related configuration."""
    
    data_root: Path = Field(default=Path("./data"), description="Root data directory")
    raw_data_path: Path = Field(default=Path("./data/raw"), description="Raw data directory")
    processed_data_path: Path = Field(default=Path("./data/processed"), description="Processed data directory")
    output_data_path: Path = Field(default=Path("./data/outputs"), description="Output data directory")
    
    @validator("data_root", "raw_data_path", "processed_data_path", "output_data_path")
    def resolve_paths(cls, v):
        """Resolve relative paths to absolute paths."""
        return v.resolve()


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class PatternSettings(BaseSettings):
    """Pattern generation configuration."""
    
    min_pattern_length: int = Field(default=3, ge=1, description="Minimum pattern length")
    max_pattern_length: int = Field(default=50, ge=1, description="Maximum pattern length")
    enable_stopword_filter: bool = Field(default=True, description="Enable stopword filtering")
    
    @validator("max_pattern_length")
    def validate_max_length(cls, v, values):
        """Validate max length is greater than min length."""
        if "min_pattern_length" in values and v <= values["min_pattern_length"]:
            raise ValueError("max_pattern_length must be greater than min_pattern_length")
        return v


class SamplingSettings(BaseSettings):
    """Sampling configuration."""
    
    dialogue_ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Ratio of dialogue samples")
    sample_size: int = Field(default=1000, ge=1, description="Total sample size")
    random_seed: int = Field(default=42, description="Random seed for reproducibility")


class ProdigySettings(BaseSettings):
    """Prodigy configuration."""
    
    db_name: str = Field(default="phonetics_anno", description="Prodigy database name")
    labels: List[str] = Field(default=["PHONETIC", "DIALECT", "SLANG"], description="Annotation labels")
    model: str = Field(default="en_core_web_sm", description="SpaCy model to use")
    host: str = Field(default="localhost", description="Prodigy host")
    port: int = Field(default=8080, ge=1, le=65535, description="Prodigy port")


class ProcessingSettings(BaseSettings):
    """Processing configuration."""
    
    batch_size: int = Field(default=1000, ge=1, description="Batch size for processing")
    max_workers: int = Field(default=4, ge=1, description="Maximum number of workers")


class Settings(BaseSettings):
    """Main settings class."""
    
    data: DataSettings = Field(default_factory=DataSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    patterns: PatternSettings = Field(default_factory=PatternSettings)
    sampling: SamplingSettings = Field(default_factory=SamplingSettings)
    prodigy: ProdigySettings = Field(default_factory=ProdigySettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
