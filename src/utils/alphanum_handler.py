import string

def to_index(val: str) -> int:
    """Convert a string (digit or uppercase letter) to an integer index."""
    if val.isdigit():
        return int(val)
    val = val.upper()
    result = 0
    for c in val:
        result = result * 26 + (ord(c) - ord('A') + 1)
    return result

def from_index(index: int, is_digit: bool) -> str:
    """Convert an integer index back to string (digit or uppercase letter range)."""
    if is_digit:
        return str(index)
    result = ''
    while index > 0:
        index, rem = divmod(index - 1, 26)
        result = chr(rem + ord('A')) + result
    return result

def alphanum_range(start: str, end: str) -> list[str]:
    """
    Generate a list from 'start' to 'end' inclusive.
    Works for both letters and digits (e.g. 'A'...'E', or '1'...'5').
    Returns an empty list if range is invalid.
    """
    if not start or not end:
        return []
    is_digit = start.isdigit() and end.isdigit()
    try:
        start_idx = to_index(start)
        end_idx = to_index(end)
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        return [from_index(i, is_digit) for i in range(start_idx, end_idx + 1)]
    except Exception:
        return []