"""Undo/Redo History Manager for dataset transformation tracking."""

import pandas as pd

from config.settings import config
from src.core.schemas import CleaningAction


class StateSnapshot:
    """Encapsulates a frozen point-in-time dataset state and metadata."""

    def __init__(self, df: pd.DataFrame, action: CleaningAction | None = None):
        self.df = df.copy()
        self.action = action


class HistoryManager:
    """Manages undo and redo stacks with bounded memory footprint."""

    def __init__(self, max_history: int | None = None):
        self.max_history = max_history or config.max_history_steps
        self.undo_stack: list[StateSnapshot] = []
        self.redo_stack: list[StateSnapshot] = []
        self.actions_log: list[CleaningAction] = []

    def record_step(self, df_before: pd.DataFrame, df_after: pd.DataFrame, action: CleaningAction) -> None:
        """Record a successful cleaning action onto the undo stack."""
        # Store state before action
        self.undo_stack.append(StateSnapshot(df_before, action))
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Clear redo stack upon new mutation
        self.redo_stack.clear()
        self.actions_log.append(action)

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self, current_df: pd.DataFrame) -> tuple[pd.DataFrame | None, CleaningAction | None]:
        """Undo last operation.

        Returns:
            (previous_df, reverted_action)
        """
        if not self.can_undo():
            return None, None

        snapshot = self.undo_stack.pop()
        # Save current state into redo stack
        self.redo_stack.append(StateSnapshot(current_df, snapshot.action))

        # Remove from active actions log
        if self.actions_log:
            self.actions_log.pop()

        return snapshot.df, snapshot.action

    def redo(self, current_df: pd.DataFrame) -> tuple[pd.DataFrame | None, CleaningAction | None]:
        """Redo last reverted operation.

        Returns:
            (restored_df, redone_action)
        """
        if not self.can_redo():
            return None, None

        snapshot = self.redo_stack.pop()
        # Push current state onto undo stack
        self.undo_stack.append(StateSnapshot(current_df, snapshot.action))
        if snapshot.action:
            self.actions_log.append(snapshot.action)

        return snapshot.df, snapshot.action

    def reset(self) -> None:
        """Clear all undo and redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.actions_log.clear()

    def get_actions(self) -> list[CleaningAction]:
        return list(self.actions_log)
