"""Export utilities for processed datasets in CSV, XLSX, and JSON formats."""

import io
from typing import Literal

import pandas as pd


class DatasetExporter:
    """Exports pandas DataFrame to memory bytes for immediate download."""

    @staticmethod
    def to_csv(df: pd.DataFrame, include_index: bool = False, encoding: str = "utf-8-sig") -> bytes:
        """Export DataFrame to CSV bytes (utf-8-sig ensures Arabic characters render in Excel)."""
        buffer = io.StringIO()
        df.to_csv(buffer, index=include_index, encoding=encoding)
        return buffer.getvalue().encode(encoding)

    @staticmethod
    def to_excel(df: pd.DataFrame, sheet_name: str = "Cleaned_Data", include_index: bool = False) -> bytes:
        """Export DataFrame to an styled XLSX workbook in memory."""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name[:31], index=include_index)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def to_json(df: pd.DataFrame, orient: Literal["records", "split", "columns"] = "records", indent: int = 2) -> bytes:
        """Export DataFrame to formatted JSON bytes."""
        json_str = df.to_json(orient=orient, date_format="iso", indent=indent, force_ascii=False)
        return json_str.encode("utf-8")
