"""Formatting utility functions."""


def format_bytes(num_bytes: float) -> str:
    """Format bytes to human-readable size string (KB, MB, GB)."""
    if num_bytes is None or num_bytes < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_number(val: float | None) -> str:
    """Format integers and floats with thousand separators."""
    if val is None:
        return "0"
    if isinstance(val, int):
        return f"{val:,}"
    if isinstance(val, float):
        return f"{val:,.2f}"
    return str(val)


def format_percentage(ratio: float | None) -> str:
    """Format ratio (0.0 to 1.0 or 0 to 100) as percentage string."""
    if ratio is None:
        return "0.0%"
    # If ratio is already > 1.0, assume it's on a 0-100 scale
    val = ratio if ratio <= 1.0 else ratio / 100.0
    return f"{val * 100:.1f}%"
