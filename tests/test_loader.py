"""Unit tests for dataset ingestion and loaders."""

import pytest

from src.io.loader import DatasetLoader
from src.utils.security import SecurityValidationError


def test_load_csv_basic():
    csv_bytes = b"id,name,val\n1,Alice,10\n2,Bob,20\n"
    df, meta = DatasetLoader.load_from_bytes(csv_bytes, "test.csv")
    assert len(df) == 2
    assert list(df.columns) == ["id", "name", "val"]
    assert meta["extension"] == "csv"
    assert meta["row_count"] == 2


def test_load_csv_semicolon_delimiter():
    csv_bytes = b"colA;colB;colC\n1;2;3\n4;5;6\n"
    df, meta = DatasetLoader.load_from_bytes(csv_bytes, "test_semi.csv")
    assert len(df) == 2
    assert len(df.columns) == 3
    assert meta["delimiter"] == ";"


def test_load_json_records():
    json_bytes = b'[{"name": "Alpha", "score": 90}, {"name": "Beta", "score": 85}]'
    df, meta = DatasetLoader.load_from_bytes(json_bytes, "records.json")
    assert len(df) == 2
    assert "name" in df.columns
    assert meta["extension"] == "json"


def test_reject_unsupported_extension():
    with pytest.raises(SecurityValidationError):
        DatasetLoader.load_from_bytes(b"some content", "dangerous.exe")


def test_empty_file_error():
    with pytest.raises(SecurityValidationError):
        DatasetLoader.load_from_bytes(b"", "empty.csv")
