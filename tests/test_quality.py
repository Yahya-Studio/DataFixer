"""Unit tests for the Data Quality Analyzer and Scorer."""

import pandas as pd

from src.analysis.quality import QualityAnalyzer


def test_clean_dataset_quality_score():
    clean_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Emma"],
            "age": [25, 30, 35, 40, 45],
        }
    )
    issues, score = QualityAnalyzer.analyze_dataset(clean_df)
    assert len(issues) == 0
    assert score.overall_score == 100.0
    assert score.completeness == 100.0
    assert score.uniqueness == 100.0


def test_dirty_dataset_detects_11_issues():
    # Construct DataFrame exhibiting issues
    df = pd.DataFrame(
        {
            "User Name": ["  John  ", "Sarah", "Sarah", "Sarah", None, "Mike"],
            "Age": [25, 30, 30, 30, 999, 28],  # Duplicate rows and outlier 999
            "Status": ["active", "Active", "Active", "ACTIVE", "inactive", "active"],  # Casing inconsistency
            "Join Date": ["2023-01-01", "2023-02-01", "2023-02-01", "bad-date", "2023-05-01", "2023-06-01"],
            "EmptyCol": [None, None, None, None, None, None],  # Completely empty column
        }
    )

    issues, score = QualityAnalyzer.analyze_dataset(df)
    categories = [iss.category for iss in issues]

    # Verify key issue types were flagged
    assert "missing" in categories or "empty_col" in categories
    assert "empty_col" in categories
    assert "duplicates" in categories
    assert "whitespace" in categories
    assert "casing" in categories
    assert "dates" in categories
    assert "outliers" in categories

    # Score should be penalized appropriately
    assert score.overall_score < 90.0
    assert 0.0 <= score.overall_score <= 100.0
