"""."""


def int_to_tuple(col: int):
    """."""
    return (col >> 16) & 0xFF, (col >> 8) & 0xFF, col & 0xFF
