"""DatasetSession encapsulates state, immutable original copy, active working copy, and audit trail."""

import uuid
from datetime import datetime
from typing import Any

import pandas as pd

from src.analysis.quality import QualityAnalyzer
from src.core.history import HistoryManager
from src.core.schemas import CleaningAction, QualityIssue, QualityScoreBreakdown


class DatasetSession:
    """Manages the full lifecycle of an active dataset session."""

    def __init__(self):
        self.session_id: str = str(uuid.uuid4())
        self.filename: str = ""
        self.file_type: str = ""
        self.file_size_bytes: int = 0
        self.upload_timestamp: datetime | None = None

        # DataFrames
        self._original_df: pd.DataFrame | None = None
        self._current_df: pd.DataFrame | None = None

        # History
        self.history: HistoryManager = HistoryManager()

        # Cached quality reports
        self.original_issues: list[QualityIssue] = []
        self.original_score: QualityScoreBreakdown | None = None

        self.current_issues: list[QualityIssue] = []
        self.current_score: QualityScoreBreakdown | None = None

    @property
    def has_data(self) -> bool:
        return self._current_df is not None and not self._current_df.empty

    @property
    def original_df(self) -> pd.DataFrame | None:
        return self._original_df

    @property
    def current_df(self) -> pd.DataFrame | None:
        return self._current_df

    def set_dataset(self, df: pd.DataFrame, metadata: dict[str, Any]) -> None:
        """Initialize session with a newly loaded dataset."""
        # Immutable original copy
        self._original_df = df.copy()
        # Working copy
        self._current_df = df.copy()

        self.filename = metadata.get("filename", "dataset")
        self.file_type = metadata.get("extension", "csv")
        self.file_size_bytes = metadata.get("size_bytes", 0)
        self.upload_timestamp = datetime.now()

        # Reset history
        self.history.reset()

        # Analyze initial quality
        self.original_issues, self.original_score = QualityAnalyzer.analyze_dataset(self._original_df)
        self.current_issues = list(self.original_issues)
        self.current_score = self.original_score

    def reanalyze_current(self) -> None:
        """Re-run quality analysis on the current working DataFrame."""
        if self._current_df is not None:
            self.current_issues, self.current_score = QualityAnalyzer.analyze_dataset(self._current_df)

    def apply_cleaning_step(
        self,
        new_df: pd.DataFrame,
        action_name: str,
        operator: str,
        target_columns: list[str] | None = None,
        parameters: dict[str, Any] | None = None,
        cells_modified: int = 0,
        description: str = "",
    ) -> CleaningAction:
        """Apply a cleaning operation, record audit trail, update current dataframe, and recalculate score."""
        if self._current_df is None:
            raise ValueError("No active dataset to clean.")

        score_before = self.current_score.overall_score if self.current_score else 0.0
        df_before = self._current_df.copy()

        # Update working DataFrame
        self._current_df = new_df.copy()

        # Re-analyze new state
        self.reanalyze_current()
        score_after = self.current_score.overall_score if self.current_score else 0.0

        # Construct audit action
        action = CleaningAction(
            action_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            name=action_name,
            operator=operator,
            target_columns=target_columns or [],
            parameters=parameters or {},
            rows_before=len(df_before),
            rows_after=len(new_df),
            cols_before=len(df_before.columns),
            cols_after=len(new_df.columns),
            cells_modified=cells_modified,
            score_before=score_before,
            score_after=score_after,
            description=description or f"{action_name} executed successfully.",
        )

        self.history.record_step(df_before, self._current_df, action)
        return action

    def undo(self) -> CleaningAction | None:
        """Undo last transformation step."""
        if self._current_df is None or not self.history.can_undo():
            return None

        previous_df, reverted_action = self.history.undo(self._current_df)
        if previous_df is not None:
            self._current_df = previous_df
            self.reanalyze_current()
        return reverted_action

    def redo(self) -> CleaningAction | None:
        """Redo last reverted transformation step."""
        if self._current_df is None or not self.history.can_redo():
            return None

        restored_df, redone_action = self.history.redo(self._current_df)
        if restored_df is not None:
            self._current_df = restored_df
            self.reanalyze_current()
        return redone_action

    def reset_to_original(self) -> None:
        """Reset current working copy back to the exact original file."""
        if self._original_df is not None:
            self._current_df = self._original_df.copy()
            self.history.reset()
            self.reanalyze_current()

    def get_diff_summary(self) -> dict[str, Any]:
        """Summarize cumulative differences between original and current dataset."""
        if self._original_df is None or self._current_df is None:
            return {}

        orig_rows = len(self._original_df)
        curr_rows = len(self._current_df)
        orig_cols = len(self._original_df.columns)
        curr_cols = len(self._current_df.columns)

        actions = self.history.get_actions()
        total_cells_modified = sum(a.cells_modified for a in actions)

        orig_score = self.original_score.overall_score if self.original_score else 0.0
        curr_score = self.current_score.overall_score if self.current_score else 0.0

        return {
            "rows_original": orig_rows,
            "rows_current": curr_rows,
            "rows_diff": curr_rows - orig_rows,
            "cols_original": orig_cols,
            "cols_current": curr_cols,
            "cols_diff": curr_cols - orig_cols,
            "total_cells_modified": total_cells_modified,
            "actions_count": len(actions),
            "score_original": orig_score,
            "score_current": curr_score,
            "score_diff": round(curr_score - orig_score, 1),
        }
