"""Date parsing, format standardization, and validation tools."""

import pandas as pd


def standardize_dates(
    df: pd.DataFrame,
    columns: list[str],
    output_format: str = "%Y-%m-%d",
    input_format: str | None = None,
) -> tuple[pd.DataFrame, int, int]:
    """Parse and standardize date representations across selected columns.

    Returns:
        (new_df, valid_dates_formatted, invalid_dates_coerced)
    """
    new_df = df.copy()
    total_formatted = 0
    total_invalid = 0

    for col in columns:
        if col not in new_df.columns:
            continue
        s = new_df[col]

        # Parse to datetime
        if input_format:
            parsed = pd.to_datetime(s, format=input_format, errors="coerce")
        else:
            parsed = pd.to_datetime(s, errors="coerce", format="mixed")

        invalid_mask = s.notna() & parsed.isna()
        valid_mask = parsed.notna()

        total_invalid += int(invalid_mask.sum())
        total_formatted += int(valid_mask.sum())

        # Format valid dates as standardized strings (or keep as datetime)
        new_df[col] = parsed.dt.strftime(output_format)
        # If output was NaT, it results in NaN in pandas
        new_df[col] = new_df[col].where(parsed.notna(), None)

    return new_df, total_formatted, total_invalid
