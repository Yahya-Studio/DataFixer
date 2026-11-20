"""Configuration settings for DataFixer application."""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    app_name: str = "DataFixer"
    version: str = "1.0.0"
    tagline: str = "Smart Data Cleaning & Quality Assurance Platform"

    # Upload limits
    max_file_size_mb: int = 50
    allowed_extensions: list[str] = Field(default_factory=lambda: ["csv", "xlsx", "xls", "json"])

    # Preview limits
    preview_rows_default: int = 15
    max_preview_rows: int = 100

    # Memory and Polars threshold (switch or optimize when row count > threshold)
    large_dataset_threshold_rows: int = 100_000

    # Quality scoring weight parameters (out of 100)
    weight_completeness: float = 30.0  # missing values & empty rows/cols
    weight_uniqueness: float = 20.0  # duplicate rows & duplicate headers
    weight_validity: float = 30.0  # data types, invalid dates, outliers
    weight_consistency: float = 20.0  # whitespace, casing, inconsistent categories

    # Outlier detection
    outlier_iqr_multiplier: float = 1.5
    outlier_zscore_threshold: float = 3.0

    # History limits
    max_history_steps: int = 25


config = AppConfig()
