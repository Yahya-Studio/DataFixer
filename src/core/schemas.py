"""Pydantic schemas and data structures for DataFixer."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QualityIssue(BaseModel):
    """Represents a discrete data quality defect found in the dataset."""

    id: str
    category: str  # missing, duplicates, headers, types, whitespace, casing, dates, empty_col, empty_row, categories, outliers
    title: str
    description: str
    affected_column: str | None = None
    affected_count: int = 0
    affected_ratio: float = 0.0
    severity: str = "medium"  # low, medium, high
    recommendation: str = ""
    sample_indices: list[int] = Field(default_factory=list)


class QualityScoreBreakdown(BaseModel):
    """Interpretable component scores constituting the total quality index."""

    overall_score: float = 100.0
    completeness: float = 100.0
    uniqueness: float = 100.0
    validity: float = 100.0
    consistency: float = 100.0

    # Penalties applied
    completeness_penalty: float = 0.0
    uniqueness_penalty: float = 0.0
    validity_penalty: float = 0.0
    consistency_penalty: float = 0.0


class DatasetProfile(BaseModel):
    """Structural profile and statistics of a dataset."""

    filename: str
    file_type: str
    file_size_bytes: int
    row_count: int
    column_count: int
    memory_usage_bytes: int
    column_names: list[str]
    column_dtypes: dict[str, str]
    duplicate_rows_count: int
    empty_rows_count: int
    empty_columns: list[str]
    total_cells: int
    total_missing_cells: int


class CleaningAction(BaseModel):
    """Audit entry recording a specific transformation performed on the dataset."""

    action_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    name: str
    operator: str
    target_columns: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    rows_before: int
    rows_after: int
    cols_before: int
    cols_after: int
    cells_modified: int = 0
    score_before: float = 0.0
    score_after: float = 0.0
    description: str = ""
