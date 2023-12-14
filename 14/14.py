import logging
import dataclasses
import io
import itertools
import math
import numpy
import re
import operator
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set, Callable

logger = logging.getLogger(__name__)


def parse_rocks(stream: io.TextIOBase) -> numpy.ndarray:
    return numpy.array([
        list(line.strip())
        for line in stream
    ])


def tilt_north(rocks: numpy.ndarray) -> numpy.ndarray:
    columns = []
    rocks = numpy.concatenate([
        [['#'] * rocks.shape[1]],
        rocks,
    ])

    columns = []
    for x in range(rocks.shape[1]):
        column = rocks[:, x]
        square_rocks = numpy.concatenate([
            numpy.flatnonzero(column == '#'),
            [rocks.shape[0] + 1],
        ])
        new_column = numpy.full(column.shape, fill_value='.')
        for top, bottom in itertools.pairwise(square_rocks):
            round_rock_count = numpy.count_nonzero(column[top:bottom] == 'O')
            new_column[top] = '#'
            new_column[top + 1:top + 1 + round_rock_count] = 'O'
        columns.append(new_column)

    rocks = numpy.c_[*columns]
    return rocks[1:]


def tilt_east(rocks: numpy.ndarray) -> numpy.ndarray:
    return numpy.rot90(tilt_north(numpy.rot90(rocks, k=1)), k=-1)


def tilt_south(rocks: numpy.ndarray) -> numpy.ndarray:
    return numpy.rot90(tilt_north(numpy.rot90(rocks, k=2)), k=-2)


def tilt_west(rocks: numpy.ndarray) -> numpy.ndarray:
    return numpy.rot90(tilt_north(numpy.rot90(rocks, k=-1)), k=1)


def iterate_rocks(rocks: numpy.ndarray) -> numpy.ndarray:
    return tilt_east(tilt_south(tilt_west(tilt_north(rocks))))


def score_rocks(rocks: numpy.ndarray) -> int:
    row_scores = numpy.arange(rocks.shape[0], 0, -1)
    row_counts = (rocks == 'O').astype(int).sum(axis=1)
    return (row_scores * row_counts).sum()


def part_one():
    rocks = parse_rocks(sys.stdin)
    print(rocks)
    rocks = tilt_north(rocks)
    print(rocks)
    print(score_rocks(rocks))


def rocks_str(rocks: numpy.ndarray) -> str:
    return '\n'.join(''.join(row) for row in rocks)


def part_two():
    rocks = parse_rocks(sys.stdin)
    seen = {}
    total_iterations = 1000000000
    for i in range(total_iterations):
        key = rocks_str(rocks)
        if key in seen:
            previous_num, previous_next = seen[key]
            cycle_length = i - previous_num
            print(f"Got identical rocks on iterations {previous_num} and {i}")
            print(f"Cycle length of {cycle_length}")

            remaining_iterations = total_iterations - i
            mod_iterations = remaining_iterations % cycle_length
            print(
                f"Remaining iterations: {remaining_iterations} "
                f"or {mod_iterations} really")
            for i in range(mod_iterations):
                rocks = iterate_rocks(rocks)
            print(score_rocks(rocks))
            return

        rocks = iterate_rocks(rocks)
        seen[key] = (i, rocks)

    print(rocks)
    print(score_rocks(rocks))


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
