import logging
import dataclasses
import io
import math
import re
import operator
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set

logger = logging.getLogger(__name__)


def parse_races_one(stream: io.TextIOBase) -> List[Tuple[int, int]]:
    time_line = stream.readline()
    assert time_line.startswith('Time: ')
    times = list(map(int, time_line[5:].split()))
    distance_line = stream.readline()
    assert distance_line.startswith('Distance: ')
    distances = list(map(int, distance_line[9:].split()))
    assert len(times) == len(distances)
    return list(zip(times, distances))


def parse_races_two(stream: io.TextIOBase) -> List[Tuple[int, int]]:
    time_line = stream.readline()
    assert time_line.startswith('Time: ')
    time = int(''.join(c for c in time_line if c.isdigit()))
    distance_line = stream.readline()
    assert distance_line.startswith('Distance: ')
    distance = int(''.join(c for c in distance_line if c.isdigit()))
    return (time, distance)


def calculate_options(race):
    time, distance = race
    s = math.sqrt(time * time - 4 * distance)
    winning_min = (time - s) / 2
    winning_max = (time + s) / 2
    if winning_min == int(winning_min):
        winning_min = int(winning_min) + 1
    if winning_max == int(winning_max):
        winning_max = int(winning_max) - 1
    options = math.floor(winning_max) - math.ceil(winning_min) + 1
    return options


def part_one():
    races = parse_races_one(sys.stdin)
    options = [calculate_options(race) for race in races]
    print(reduce(operator.mul, options, 1))


def part_two():
    race = parse_races_two(sys.stdin)
    print(calculate_options(race))


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
