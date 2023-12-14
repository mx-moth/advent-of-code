import io
import dataclasses
import operator
import sys
import string
from functools import reduce
from typing import Optional, Tuple, List


@dataclasses.dataclass
class Part:
    symbol: int
    x: int
    y: int


@dataclasses.dataclass
class Number:
    number: int
    x1: int
    x2: int
    y: int

    def is_adjacent(self, part: Part) -> bool:
        return (
            (self.x1 - 1) <= part.x
            and (self.x2 + 1) >= part.x
            and (self.y - 1) <= part.y
            and (self.y + 1) >= part.y
        )


@dataclasses.dataclass
class peekable:
    stream: io.TextIOBase
    _next: Optional[str] = None

    def next(self):
        if self._next is not None:
            value = self._next
            self._next = None
            return value
        return self.stream.read(1)

    def peek(self):
        if self._next is None:
            self._next = self.stream.read(1)
        return self._next

    def __bool__(self):
        return self.peek() != ''


def parse_schematic(stream: io.TextIOBase) -> Tuple[List[Number], List[Part]]:
    x = 0
    y = 0
    numbers = []
    parts = []

    chars = peekable(stream)
    while chars:
        char = chars.next()
        x += 1
        if char == '\n':
            x = 0
            y += 1
            continue
        elif char == '.':
            continue
        elif char in string.digits:
            x1 = x
            digits = char
            while chars.peek() in string.digits:
                digits += chars.next()
                x += 1
            part_number = Number(
                number=int(digits),
                x1=x1,
                x2=x,
                y=y
            )
            numbers.append(part_number)
            continue
        else:
            part = Part(symbol=char, x=x, y=y)
            parts.append(part)
    return numbers, parts


def part_one():
    numbers, parts = parse_schematic(sys.stdin)
    part_numbers = [
        number for number in numbers
        if any(number.is_adjacent(part) for part in parts)
    ]
    print(sum(p.number for p in part_numbers))


def part_two():
    numbers, parts = parse_schematic(sys.stdin)
    result = 0
    for part in parts:
        if part.symbol != '*':
            continue
        part_numbers = [number for number in numbers if number.is_adjacent(part)]
        if len(part_numbers) != 2:
            continue
        result += reduce(operator.mul, (p.number for p in part_numbers))

    print(result)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} (one|two)")
        sys.exit(1)

    if sys.argv[1] == 'one':
        part_one()
    elif sys.argv[1] == 'two':
        part_two()
    else:
        print(f"usage: {sys.argv[0]} (one|two)")
        sys.exit(1)
