import logging
import collections
import enum
import dataclasses
import io
import math
import re
import operator
import sys
from functools import reduce, cached_property
from typing import Optional, Tuple, List, Set, Any

logger = logging.getLogger(__name__)


class HandType(enum.IntEnum):
    high_card = 1
    one_pair = 2
    two_pair = 3
    three_of_a_kind = 4
    full_house = 5
    four_of_a_kind = 6
    five_of_a_kind = 7


@dataclasses.dataclass
class Hand:
    cards: str
    bid: int

    @cached_property
    def hand_type(self) -> HandType:
        counts = sorted(collections.Counter(self.cards).values(), reverse=True)
        if counts == [5]:
            return HandType.five_of_a_kind
        if counts == [4, 1]:
            return HandType.four_of_a_kind
        if counts == [3, 2]:
            return HandType.full_house
        if counts == [3, 1, 1]:
            return HandType.three_of_a_kind
        if counts == [2, 2, 1]:
            return HandType.two_pair
        if counts == [2, 1, 1, 1]:
            return HandType.one_pair
        return HandType.high_card

    @cached_property
    def card_ranks(self) -> Tuple[int, int, int, int, int]:
        return tuple(card_order[c] for c in self.cards)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        return (self.hand_type, self.card_ranks) < (other.hand_type, other.card_ranks)


card_order = {
    card: rank for rank, card in enumerate(reversed('AKQJT98765432'))
}


def parse_hands(stream: io.TextIOBase) -> List[Hand]:
    hands = []
    for line in stream:
        cards, bid = line.split()
        hands.append(Hand(cards, int(bid)))
    return hands



def part_one():
    hands = parse_hands(sys.stdin)
    sorted_hands = sorted(hands)
    print(sum(i * hand.bid for i, hand in enumerate(sorted_hands, start=1)))


def part_two():
    pass


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
