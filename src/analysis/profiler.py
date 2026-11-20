"""Dataset profiler for statistical overviews and column-level distributions."""

from typing import Any

import pandas as pd

from src.core.schemas import DatasetProfile


class DatasetProfiler:
    """Computes full schema profiles, memory footprints, and column summaries."""

    @classmethod
    def profile_dataframe(cls, df: pd.DataFrame, filename: str = "dataset", file_size_bytes: int = 0) -> DatasetProfile:
        """Generate high-level profile of the dataset."""
        row_count = len(df)
        col_count = len(df.columns)
        total_cells = row_count * col_count

        # Memory usage
        memory_usage_bytes = int(df.memory_usage(deep=True).sum()) if row_count > 0 else 0

        # Data types map
        dtypes_map = {col: str(df[col].dtype) for col in df.columns}

        # Empty columns & empty rows
        empty_cols = [str(c) for c in df.columns if df[c].isna().all()]
        empty_rows = int(df.isna().all(axis=1).sum()) if row_count > 0 else 0

        # Duplicate rows
        dup_rows = int(df.duplicated().sum()) if row_count > 0 else 0

        # Total missing cells
        missing_cells = int(df.isna().sum().sum()) if row_count > 0 else 0

        # Extension
        ext = filename.split(".")[-1].lower() if "." in filename else "csv"

        return DatasetProfile(
            filename=filename,
            file_type=ext,
            file_size_bytes=file_size_bytes or memory_usage_bytes,
            row_count=row_count,
            column_count=col_count,
            memory_usage_bytes=memory_usage_bytes,
            column_names=[str(c) for c in df.columns],
            column_dtypes=dtypes_map,
            duplicate_rows_count=dup_rows,
            empty_rows_count=empty_rows,
            empty_columns=empty_cols,
            total_cells=total_cells,
            total_missing_cells=missing_cells,
        )

    @classmethod
    def get_column_summary(cls, series: pd.Series) -> dict[str, Any]:
        """Produce deep statistics for a single column based on its type."""
        count = len(series)
        null_count = int(series.isna().sum())
        non_null = count - null_count
        unique_count = int(series.nunique(dropna=True))

        summary: dict[str, Any] = {
            "name": str(series.name),
            "dtype": str(series.dtype),
            "total_count": count,
            "null_count": null_count,
            "null_percentage": (null_count / count * 100) if count > 0 else 0.0,
            "unique_count": unique_count,
            "unique_percentage": (unique_count / non_null * 100) if non_null > 0 else 0.0,
        }

        if pd.api.types.is_numeric_dtype(series):
            clean_s = series.dropna()
            if len(clean_s) > 0:
                summary.update(
                    {
                        "mean": float(clean_s.mean()),
                        "std": float(clean_s.std()) if len(clean_s) > 1 else 0.0,
                        "min": float(clean_s.min()),
                        "q25": float(clean_s.quantile(0.25)),
                        "median": float(clean_s.median()),
                        "q75": float(clean_s.quantile(0.75)),
                        "max": float(clean_s.max()),
                    }
                )
        elif pd.api.types.is_string_dtype(series) or series.dtype == object:
            clean_s = series.dropna().astype(str)
            if len(clean_s) > 0:
                top_counts = clean_s.value_counts().head(5).to_dict()
                summary["top_values"] = top_counts
                summary["min_length"] = int(clean_s.str.len().min())
                summary["max_length"] = int(clean_s.str.len().max())
                summary["avg_length"] = float(clean_s.str.len().mean())

        return summary
