import string
import sys

def line_number(line: str) -> int:
    digits = [d for d in line if d in string.digits]
    return int(digits[0] + digits[-1])

print(sum(map(line_number, sys.stdin)))
