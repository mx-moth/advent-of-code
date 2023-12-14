import sys

digit_strings = {
    **{str(d): d for d in [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}

def line_number(line: str) -> int:
    first = min(
        (pos, digit, text)
        for text, digit in digit_strings.items()
        if (pos := line.find(text)) != -1
    )
    last = max(
        (pos, digit, text)
        for text, digit in digit_strings.items()
        if (pos := line.rfind(text)) != -1
    )
    return first[1] * 10 + last[1]

print(sum(map(line_number, sys.stdin)))
