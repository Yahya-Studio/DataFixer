"""Unit tests for report generators and dataset export formats."""

import pandas as pd

from src.core.state import DatasetSession
from src.io.exporter import DatasetExporter
from src.reports.generator import build_report_data
from src.reports.html_report import generate_html_report
from src.reports.pdf_report import generate_pdf_report


def test_export_formats():
    df = pd.DataFrame({"Name": ["أحمد", "Sara"], "Score": [95, 88]})

    # CSV
    csv_bytes = DatasetExporter.to_csv(df)
    assert len(csv_bytes) > 0
    assert "Sara" in csv_bytes.decode("utf-8-sig")

    # Excel
    xlsx_bytes = DatasetExporter.to_excel(df)
    assert len(xlsx_bytes) > 0
    assert xlsx_bytes[:4] == b"PK\x03\x04"  # Zip/Excel signature

    # JSON
    json_bytes = DatasetExporter.to_json(df)
    assert len(json_bytes) > 0
    assert "Sara" in json_bytes.decode("utf-8")


def test_html_and_pdf_reports():
    session = DatasetSession()
    df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", "z"]})
    session.set_dataset(df, {"filename": "data.csv", "size_bytes": 120})

    report_data = build_report_data(session)
    assert report_data["filename"] == "data.csv"

    # HTML
    html = generate_html_report(report_data)
    assert "DataFixer" in html
    assert "data.csv" in html

    # PDF
    pdf_bytes = generate_pdf_report(report_data)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")


def test_pdf_report_with_arabic_content():
    session = DatasetSession()
    df = pd.DataFrame({"الاسم": ["أحمد", "سارة"], "الراتب": [5000, 6000]})
    session.set_dataset(df, {"filename": "بيانات_الموظفين.xlsx", "size_bytes": 1024})

    # Apply Arabic action
    session.apply_cleaning_step(
        new_df=df,
        action_name="توحيد حالة الأحرف والأسماء",
        operator="normalize",
        target_columns=["الاسم"],
        description="تم التوحيد بنجاح",
    )

    report_data = build_report_data(session)
    pdf_bytes = generate_pdf_report(report_data)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
