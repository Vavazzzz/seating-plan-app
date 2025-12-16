import re

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
    
# Alphanumeric sorting helper
def alphanum_sort_key(value: str):
    # Extract leading digits, trailing digits, and letters
    match = re.match(r'^(\D*)(\d+)(\D*)$', value)
    if match:
        prefix, num, suffix = match.groups()
        # Sort by: prefix, then number, then suffix
        return (0, prefix, int(num), suffix)
    
    # Try pure numeric
    try:
        return (0, "", int(value), "")
    except ValueError:
        pass
    
    # Try extract any numbers from the middle/end
    nums = re.findall(r'\d+', value)
    if nums:
        # has some numbers: sort by first number found, then the string
        return (1, int(nums[0]), value)
    
    # Pure alpha or other: sort lexicographically last
    return (2, value, 0, "")