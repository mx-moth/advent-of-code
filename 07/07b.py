import logging
import collections
import enum
import dataclasses
import io
import sys
from functools import cached_property
from typing import Tuple, List, Any

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
        # Count common cards
        counts = collections.Counter(self.cards)
        if 'J' in counts and counts.keys():
            # If there is a joker in the deck, remove it and put its count
            # towards the highest card total. Hands are ordered such that
            # having more of one card is always the best option, so adding
            # jokers to the highest remaining card total will always give the
            # best hand.
            total_j = counts.pop('J')
            if not counts:
                # ... except if the hand was five jokers, at which point
                # `counts` is now empty.
                counts['J'] = total_j
            else:
                max_card = max(counts.items(), key=lambda x: x[1])[0]
                counts[max_card] += total_j

        counts = sorted(counts.values(), reverse=True)
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
    card: rank for rank, card in enumerate(reversed('AKQT98765432J'))
}


def parse_hands(stream: io.TextIOBase) -> List[Hand]:
    hands = []
    for line in stream:
        cards, bid = line.split()
        hands.append(Hand(cards, int(bid)))
    return hands



def part_one():
    pass


def part_two():
    hands = parse_hands(sys.stdin)
    sorted_hands = sorted(hands)
    print(sum(i * hand.bid for i, hand in enumerate(sorted_hands, start=1)))


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
