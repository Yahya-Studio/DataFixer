"""Robust dataset loader supporting CSV, Excel, and JSON with auto-encoding & sheet discovery."""

import csv
import io
import json
from pathlib import Path
from typing import Any

import charset_normalizer
import openpyxl
import pandas as pd

from src.utils.security import SecurityValidationError, sanitize_filename, validate_file_metadata


class DataLoaderError(Exception):
    """User-friendly data loading exception."""


class DatasetLoader:
    """Handles parsing and ingestion of uploaded datasets without mutating inputs."""

    @staticmethod
    def inspect_excel_sheets(file_bytes: bytes) -> list[str]:
        """Inspect and return available sheet names in an Excel workbook."""
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
            sheets = wb.sheetnames
            wb.close()
            return sheets
        except Exception as e:
            raise DataLoaderError(f"تعذر قراءة مصنف Excel: {e!s}") from e

    @staticmethod
    def detect_csv_encoding_and_delimiter(file_bytes: bytes) -> tuple[str, str]:
        """Detect the encoding and separator of a CSV file byte payload."""
        sample_size = min(len(file_bytes), 64 * 1024)
        sample = file_bytes[:sample_size]

        # 1. Encoding detection
        encoding = "utf-8"
        try:
            detected = charset_normalizer.from_bytes(sample).best()
            if detected and detected.encoding:
                encoding = detected.encoding
        except Exception:
            encoding = "utf-8"

        # Try decoding sample
        text_sample = ""
        for enc in [encoding, "utf-8-sig", "utf-8", "cp1256", "windows-1256", "iso-8859-1", "latin1"]:
            try:
                text_sample = sample.decode(enc)
                encoding = enc
                break
            except UnicodeDecodeError:
                continue

        # 2. Delimiter detection
        delimiter = ","
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text_sample[:4096], delimiters=[",", ";", "\t", "|"])
            delimiter = dialect.delimiter
        except Exception:
            # Fallback heuristic: count common separators in first non-empty lines
            lines = [line.strip() for line in text_sample.splitlines() if line.strip()][:5]
            if lines:
                candidate_counts = {sep: sum(line.count(sep) for line in lines) for sep in [",", ";", "\t", "|"]}
                best = max(candidate_counts, key=candidate_counts.get)
                if candidate_counts[best] > 0:
                    delimiter = best

        return encoding, delimiter

    @classmethod
    def load_from_bytes(
        cls,
        file_bytes: bytes,
        filename: str,
        sheet_name: str | None = None,
        encoding: str | None = None,
        delimiter: str | None = None,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Load tabular data from raw bytes into a clean pandas DataFrame.

        Returns:
            Tuple of (DataFrame, metadata_dict)
        """
        clean_name = sanitize_filename(filename)
        is_valid, err = validate_file_metadata(clean_name, len(file_bytes))
        if not is_valid:
            raise SecurityValidationError(err)

        ext = Path(clean_name).suffix.lstrip(".").lower()
        metadata: dict[str, Any] = {
            "filename": clean_name,
            "extension": ext,
            "size_bytes": len(file_bytes),
            "sheet_name": sheet_name,
        }

        try:
            if ext == "csv":
                detected_enc, detected_delim = cls.detect_csv_encoding_and_delimiter(file_bytes)
                enc_to_use = encoding or detected_enc
                delim_to_use = delimiter or detected_delim
                metadata["encoding"] = enc_to_use
                metadata["delimiter"] = delim_to_use

                df = pd.read_csv(
                    io.BytesIO(file_bytes),
                    encoding=enc_to_use,
                    sep=delim_to_use,
                    low_memory=False,
                    on_bad_lines="skip",
                )

            elif ext in ("xlsx", "xls"):
                sheets = cls.inspect_excel_sheets(file_bytes)
                metadata["available_sheets"] = sheets
                selected_sheet = sheet_name if (sheet_name and sheet_name in sheets) else (sheets[0] if sheets else 0)
                metadata["sheet_name"] = selected_sheet

                df = pd.read_excel(
                    io.BytesIO(file_bytes),
                    sheet_name=selected_sheet,
                )

            elif ext == "json":
                # JSON can be records, split, columns, or values
                try:
                    df = pd.read_json(io.BytesIO(file_bytes))
                except ValueError:
                    # Try json.loads to normalize nested dictionaries/records
                    raw_json = json.loads(file_bytes.decode("utf-8", errors="replace"))
                    if isinstance(raw_json, list):
                        df = pd.json_normalize(raw_json)
                    elif isinstance(raw_json, dict):
                        # Find the first list value, or normalize the dict itself
                        list_keys = [k for k, v in raw_json.items() if isinstance(v, list)]
                        if list_keys:
                            df = pd.json_normalize(raw_json[list_keys[0]])
                        else:
                            df = pd.DataFrame([raw_json])
                    else:
                        raise DataLoaderError("بنية ملف JSON غير صالحة للتحويل إلى جدول.")

            else:
                raise DataLoaderError(f"صيغة الملف {ext} غير مدعومة.")

            # Basic post-load hygiene: ensure columns are strings
            df.columns = [str(c).strip() if pd.notna(c) else f"Unnamed_{i}" for i, c in enumerate(df.columns)]

            metadata["row_count"] = len(df)
            metadata["column_count"] = len(df.columns)
            return df, metadata

        except SecurityValidationError, DataLoaderError:
            raise
        except Exception as e:
            raise DataLoaderError(f"فشل أثناء قراءة الملف '{clean_name}': {e!s}") from e
