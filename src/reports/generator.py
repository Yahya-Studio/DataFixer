"""Aggregates session information into a unified report model."""

from datetime import datetime
from typing import Any

from src.core.state import DatasetSession
from src.utils.formatting import format_bytes, format_number


def build_report_data(session: DatasetSession) -> dict[str, Any]:
    """Compile complete audit summary from a DatasetSession."""
    diff = session.get_diff_summary()
    actions = session.history.get_actions()

    return {
        "report_id": session.session_id,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": session.filename,
        "file_type": session.file_type.upper(),
        "file_size": format_bytes(session.file_size_bytes),
        "upload_time": session.upload_timestamp.strftime("%Y-%m-%d %H:%M:%S") if session.upload_timestamp else "-",
        "rows_before": format_number(diff.get("rows_original", 0)),
        "rows_after": format_number(diff.get("rows_current", 0)),
        "rows_diff": diff.get("rows_diff", 0),
        "cols_before": diff.get("cols_original", 0),
        "cols_after": diff.get("cols_current", 0),
        "cols_diff": diff.get("cols_diff", 0),
        "cells_modified": format_number(diff.get("total_cells_modified", 0)),
        "initial_score": diff.get("score_original", 0.0),
        "final_score": diff.get("score_current", 0.0),
        "score_improvement": diff.get("score_diff", 0.0),
        "original_score_breakdown": session.original_score,
        "final_score_breakdown": session.current_score,
        "detected_issues": session.original_issues,
        "remaining_issues": session.current_issues,
        "actions_log": actions,
    }
