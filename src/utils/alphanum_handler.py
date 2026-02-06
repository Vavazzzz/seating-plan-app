import re

def to_index(val: str) -> int:
    """Convert a string (digit or uppercase letter/letters) to an integer index.
    Supports single letters (A-Z) and multi-letter sequences (AA, AB, ... BA, BB, etc)."""
    if val.isdigit():
        return int(val)
    val = val.upper()
    result = 0
    for c in val:
        result = result * 26 + (ord(c) - ord('A') + 1)
    return result

def from_index(index: int, is_digit: bool) -> str:
    """Convert an integer index back to string (digit or uppercase letter range).
    For letters, generates A-Z, then AA-AZ, BA-BZ, CA-CZ, etc."""
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
    Works for both letters and digits (e.g. 'A'...'Z', 'AA'...'AC', or '1'...'5').
    Supports multi-letter ranges: A-Z, then AA-AZ, BA-BZ, CA-CZ, etc.
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
    
    # Pure alpha: use base-26 index so single letters (1-26) sort before double letters (27+)
    if value.isalpha():
        return (2, to_index(value.upper()), "")
    
    # Other: sort last
    return (3, value, 0, "")

if __name__ == "__main__":
    # Example usage
    lst = ["AA", "AB", "AC", "A", "B", "C", "1", "2", "10", "A1", "A10", "B2"]
    for l in lst:
        #print(l, ", ", alphanum_sort_key(l))
        print(type(alphanum_sort_key(l)), alphanum_sort_key(l))