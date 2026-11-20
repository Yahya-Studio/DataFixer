"""Unit tests for the modular data cleaning operators."""

import pandas as pd

from src.cleaning.columns import (
    drop_empty_columns,
    standardize_column_names,
)
from src.cleaning.dates import standardize_dates
from src.cleaning.duplicates import remove_duplicates
from src.cleaning.missing import drop_missing_values, fill_missing_values
from src.cleaning.outliers import handle_outliers
from src.cleaning.text import (
    change_case,
    find_and_replace,
    strip_and_normalize_whitespace,
)


def test_missing_drop_and_fill():
    df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", None]})

    # Drop any null
    dropped, removed, _cells = drop_missing_values(df, how="any")
    assert len(dropped) == 1
    assert removed == 2

    # Fill median
    filled_num, _cells_num = fill_missing_values(df, columns=["A"], strategy="median")
    assert filled_num["A"].isna().sum() == 0
    assert filled_num.loc[1, "A"] == 2.0

    # Fill mode
    filled_cat, _cells_cat = fill_missing_values(df, columns=["B"], strategy="custom", fill_value="Unknown")
    assert filled_cat["B"].isna().sum() == 0
    assert filled_cat.loc[2, "B"] == "Unknown"


def test_remove_duplicates():
    df = pd.DataFrame({"A": [1, 1, 2], "B": ["a", "a", "b"]})
    clean_df, removed = remove_duplicates(df, keep="first")
    assert len(clean_df) == 2
    assert removed == 1


def test_text_strip_and_case():
    df = pd.DataFrame({"text": ["  hello world  ", "FOO   BAR", "test"]})
    stripped, _cells_s = strip_and_normalize_whitespace(df, ["text"], remove_inner_extra=True)
    assert stripped.loc[0, "text"] == "hello world"
    assert stripped.loc[1, "text"] == "FOO BAR"

    upper_df, _cells_u = change_case(stripped, ["text"], "upper")
    assert upper_df.loc[0, "text"] == "HELLO WORLD"


def test_find_and_replace():
    df = pd.DataFrame({"desc": ["Price: $50", "Price: $100"]})
    res, count = find_and_replace(df, ["desc"], "$", "USD ")
    assert res.loc[0, "desc"] == "Price: USD 50"
    assert count == 2


def test_column_operations():
    df = pd.DataFrame({"User Name": [1, 2], "Empty": [None, None]})

    # Standardize column names to snake_case
    clean_df, _cnt = standardize_column_names(df, style="snake_case")
    assert "user_name" in clean_df.columns

    # Drop empty columns
    no_empty, dropped = drop_empty_columns(clean_df)
    assert "empty" not in no_empty.columns
    assert "empty" in dropped


def test_dates_and_outliers():
    df = pd.DataFrame(
        {
            "date_str": ["2023-01-05", "05/01/2023", "corrupt", "2023-02-01", "2023-03-01"],
            "vals": [10, 12, 11, 1000, 11],  # 1000 is an outlier
        }
    )

    # Dates
    dates_df, _val_cnt, _inv_cnt = standardize_dates(df, ["date_str"], output_format="%Y-%m-%d")
    assert dates_df.loc[0, "date_str"] == "2023-01-05"
    assert pd.isna(dates_df.loc[2, "date_str"])

    # Outlier clipping
    out_df, affected, _ = handle_outliers(df, "vals", action="clip")
    assert affected >= 1
    assert out_df["vals"].max() < 1000
