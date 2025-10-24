import string

def to_index(val):
        if val.isdigit():
            return int(val)
        else:
            val = val.upper()
            result = 0
            for c in val:
                result = result * 26 + (ord(c) - ord('A') + 1)
            return result
        
def from_index(index, is_digit):
        if is_digit:
            return str(index)
        result = ''
        while index > 0:
            index, rem = divmod(index - 1, 26)
            result = chr(rem + ord('A')) + result
        return result

def alphanum_range(start: str, end: str) -> list[str]:
    """Generate a list from 'start' to 'end' inclusive. Works for both letters and digits."""
    
    is_digit = start.isdigit() and end.isdigit()
    start_idx = to_index(start)
    end_idx = to_index(end)
    return [from_index(i, is_digit) for i in range(start_idx, end_idx + 1)]


