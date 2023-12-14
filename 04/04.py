import dataclasses
import io
import re
import operator
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set


@dataclasses.dataclass
class Card:
    number: int
    winning_numbers: Set[int]
    numbers_you_have: Set[int]

    def matches(self) -> int:
        return len(self.winning_numbers & self.numbers_you_have)

    def score(self) -> int:
        matches = self.matches()
        if matches == 0:
            return 0
        return int(2 ** (matches - 1))


class CopyTracker:
    def __init__(self):
        self.buffer = []

    def pop(self) -> int:
        if self.buffer:
            return self.buffer.pop(0)
        return 1

    def add_matches(self, matches: int, copies: int) -> None:
        for index in range(matches):
            if len(self.buffer) <= index:
                self.buffer.extend([copies + 1] * (matches - index))
                return
            else:
                self.buffer[index] += copies


CARD_RE = re.compile(r'Card +(\d+): ')

def parse_card(line: str) -> Card:
    card_match = CARD_RE.match(line)
    if card_match is None:
        raise ValueError(f"Invalid line: {line!r}")
    card_number = int(card_match[1])
    line = line[card_match.end():]
    winning_numbers_string, numbers_you_have_string = line.split('|', 2)
    winning_numbers = set(map(int, winning_numbers_string.split()))
    numbers_you_have = set(map(int, numbers_you_have_string.split()))
    return Card(card_number, winning_numbers, numbers_you_have)


def parse_cards(stream: io.TextIOBase):
    for line in stream:
        yield parse_card(line.rstrip('\n'))


def part_one():
    cards = parse_cards(sys.stdin)
    result = sum(card.score() for card in cards)
    print(result)


def part_two():
    cards = parse_cards(sys.stdin)
    copies = CopyTracker()
    total_cards = 0
    for card in cards:
        count = copies.pop()
        matches = card.matches()
        copies.add_matches(matches, count)
        total_cards += count
    print(total_cards)


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
