"""Unit tests for SessionState, Undo/Redo history, and non-mutation integrity."""

import pandas as pd

from src.cleaning.duplicates import remove_duplicates
from src.core.state import DatasetSession


def test_session_lifecycle_and_undo_redo():
    session = DatasetSession()
    initial_df = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "x", "y"]})

    session.set_dataset(initial_df, {"filename": "test.csv", "size_bytes": 100})
    assert session.has_data
    assert len(session.current_df) == 3

    # Apply duplicate removal
    cleaned_df, removed = remove_duplicates(session.current_df)
    session.apply_cleaning_step(
        new_df=cleaned_df,
        action_name="حذف تكرارات",
        operator="remove_duplicates",
        cells_modified=removed,
    )

    assert len(session.current_df) == 2
    assert session.history.can_undo()

    # Original dataframe must NOT be mutated!
    assert len(session.original_df) == 3

    # Undo
    session.undo()
    assert len(session.current_df) == 3
    assert session.history.can_redo()

    # Redo
    session.redo()
    assert len(session.current_df) == 2


def test_session_reset_to_original():
    session = DatasetSession()
    initial_df = pd.DataFrame({"A": [1, 2, 3]})
    session.set_dataset(initial_df, {"filename": "nums.csv"})

    # Modify
    session.apply_cleaning_step(
        new_df=pd.DataFrame({"A": [1]}),
        action_name="تصفية",
        operator="filter",
    )
    assert len(session.current_df) == 1

    # Reset
    session.reset_to_original()
    assert len(session.current_df) == 3
    assert not session.history.can_undo()
