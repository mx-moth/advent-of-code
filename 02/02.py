import dataclasses
import enum
import operator
import re
import sys
from functools import reduce
from typing import Iterable, List, Dict


class Colour(str, enum.Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


@dataclasses.dataclass
class Game:
    number: int
    draws: List[Dict[Colour, int]]


GAME_RE = re.compile(r'^Game (\d+): ')
DRAW_RE = re.compile(r'([^;]*)(?:; |$)')
CUBE_RE = re.compile(r'(\d+) (' + '|'.join(re.escape(c) for c in Colour) + ')(?:, |$)')


def consume_re(pattern: re.Pattern, string: str) -> Iterable[re.Match]:
    while string:
        match = pattern.match(string)
        if match is None:
            raise ValueError(
                f"Pattern {pattern} did not match beginning of string {string!r}!")
        yield match
        string = string[match.end():]


def parse_line(line: str) -> Game:
    line = line.rstrip('\n')
    game_match = GAME_RE.match(line)
    game_number = int(game_match[1])
    line = line[game_match.end():]
    draws = [
        {
            Colour(cube_match[2]): int(cube_match[1])
            for cube_match in consume_re(CUBE_RE, draw_match[1])
        }
        for draw_match in consume_re(DRAW_RE, line)
    ]
    return Game(game_number, draws)


def is_possible(game: Game, contents: Dict[Colour, int]) -> bool:
    return all(
        all(
            contents[colour] >= count
            for colour, count in draw.items()
        )
        for draw in game.draws
    )

def power(game) -> int:
    counts = {c: 0 for c in Colour}
    for draw in game.draws:
        for colour, count in draw.items():
            if counts[colour] < count:
                counts[colour] = count
    return reduce(operator.mul, counts.values())


def part_one():
    contents = {
        Colour.RED: 12,
        Colour.GREEN: 13,
        Colour.BLUE: 14,
    }

    games = list(map(parse_line, sys.stdin))

    result = sum(
        game.number for game in games
        if is_possible(game, contents)
    )
    print(result)


def part_two():
    games = list(map(parse_line, sys.stdin))
    result = sum(map(power, games))
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
