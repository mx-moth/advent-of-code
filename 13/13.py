import logging
import collections
import io
import math
import numpy
import re
import operator
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set, Iterable

logger = logging.getLogger(__name__)


def parse_terrain(stream: io.TextIOBase) -> Iterable[numpy.ndarray]:
    block = []
    while True:
        line = stream.readline()
        if line == '\n' or line == '':
            yield (numpy.array(block) == '#').astype(int)
            if line == '\n':
                block = []
            else:
                break
        else:
            block.append(list(line.strip()))


def mirror_points_for_line(line: numpy.ndarray) -> set[int]:
    mirror_points = set()
    length = len(line)
    for i in range(1, length):
        segment_length = min(i, length - i)
        left = line[max(0, i - segment_length):i]
        right = line[i:min(length, i + segment_length)]
        if numpy.array_equal(left, right[::-1]):
            mirror_points.add(i)
    return mirror_points


def mirror_counts_for_block(
    block: numpy.ndarray,
) -> tuple[
    list[set[int]],
    collections.Counter[int],
]:
    all_mirror_points = []
    counts = collections.Counter()
    for line in block:
        mirror_points = mirror_points_for_line(line)
        all_mirror_points.append(mirror_points)
        counts.update(mirror_points)

    return all_mirror_points, counts


def mirror_points_for_block(block: numpy.ndarray) -> set[int]:
    sets, counts = mirror_counts_for_block(block)
    return set.intersection(*sets)


def score_for_block(block: numpy.ndarray) -> int:
    vertical = mirror_points_for_block(block)
    if vertical:
        column = vertical.pop()
        print(f"Mirrorred vertically around column {column}")
        return column
    horizontal = mirror_points_for_block(block.T)
    if horizontal:
        row = horizontal.pop()
        print(f"Mirrorred horizontal around row {row}")
        return row * 100
    raise ValueError(f"Could not find mirror for block\n{block}")


def find_smudge_for_block(
    block: numpy.ndarray,
) -> tuple[int, tuple[int, int]] | None:
    sets, counts = mirror_counts_for_block(block)

    # Looking for a count of one less than the size.
    # This indicates a position where the mirror _almost_ worked.
    expected_count = block.shape[0] - 1
    for position, count in counts.items():
        if count == expected_count:
            smudged_row = next(
                i for i, s in enumerate(sets)
                if position not in s)
            smudged_line = block[smudged_row]

            for i in range(block.shape[1]):
                fixed_line = smudged_line.copy()
                fixed_line[i] = 1 - fixed_line[i]
                if position in mirror_points_for_line(fixed_line):
                    return position, (smudged_row, i)


def score_for_smudged_block(block: numpy.ndarray) -> int:
    results = find_smudge_for_block(block)
    if results is not None:
        column, smudge = results
        return column

    results = find_smudge_for_block(block.T)
    if results is not None:
        row, smudge = results
        return row * 100

    raise ValueError("Could not find smudge for block!")


def part_one():
    total_score = 0
    for block in parse_terrain(sys.stdin):
        print(block)
        score = score_for_block(block)
        total_score += score
    print(total_score)


def part_two():
    total_score = 0
    for block in parse_terrain(sys.stdin):
        score = score_for_smudged_block(block)
        total_score += score
    print(total_score)


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
