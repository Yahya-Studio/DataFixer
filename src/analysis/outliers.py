"""Outlier detection algorithms using IQR and Z-Score methods."""

from typing import NamedTuple

import numpy as np
import pandas as pd

from config.settings import config


class OutlierSummary(NamedTuple):
    column: str
    method: str
    count: int
    ratio: float
    lower_bound: float
    upper_bound: float
    sample_indices: list[int]
    sample_values: list[float]


def detect_outliers_iqr(series: pd.Series, multiplier: float | None = None) -> OutlierSummary | None:
    """Detect outliers in a numeric pandas Series using Interquartile Range (IQR)."""
    clean_s = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_s) < 5:
        return None

    mult = multiplier if multiplier is not None else config.outlier_iqr_multiplier
    q1 = clean_s.quantile(0.25)
    q3 = clean_s.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return None

    lower_bound = q1 - mult * iqr
    upper_bound = q3 + mult * iqr

    outlier_mask = (clean_s < lower_bound) | (clean_s > upper_bound)
    count = int(outlier_mask.sum())
    if count == 0:
        return None

    indices = clean_s[outlier_mask].index.tolist()
    sample_indices = indices[:10]
    sample_values = clean_s[outlier_mask].iloc[:10].tolist()

    return OutlierSummary(
        column=str(series.name),
        method="IQR",
        count=count,
        ratio=count / len(clean_s),
        lower_bound=float(lower_bound),
        upper_bound=float(upper_bound),
        sample_indices=sample_indices,
        sample_values=[round(v, 2) for v in sample_values],
    )


def detect_outliers_zscore(series: pd.Series, threshold: float | None = None) -> OutlierSummary | None:
    """Detect outliers using standard Z-Score."""
    clean_s = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_s) < 5:
        return None

    thresh = threshold if threshold is not None else config.outlier_zscore_threshold
    mean = clean_s.mean()
    std = clean_s.std()

    if std == 0 or np.isnan(std):
        return None

    z_scores = np.abs((clean_s - mean) / std)
    outlier_mask = z_scores > thresh
    count = int(outlier_mask.sum())
    if count == 0:
        return None

    indices = clean_s[outlier_mask].index.tolist()
    sample_indices = indices[:10]
    sample_values = clean_s[outlier_mask].iloc[:10].tolist()

    return OutlierSummary(
        column=str(series.name),
        method="Z-Score",
        count=count,
        ratio=count / len(clean_s),
        lower_bound=float(mean - thresh * std),
        upper_bound=float(mean + thresh * std),
        sample_indices=sample_indices,
        sample_values=[round(v, 2) for v in sample_values],
    )


def scan_all_numeric_outliers(df: pd.DataFrame, method: str = "iqr") -> dict[str, OutlierSummary]:
    """Scan all numeric columns in a DataFrame for statistical anomalies/outliers."""
    results = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        summary = detect_outliers_iqr(df[col]) if method.lower() == "iqr" else detect_outliers_zscore(df[col])
        if summary and summary.count > 0:
            results[col] = summary
    return results
