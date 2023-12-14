import logging
import itertools
import dataclasses
import io
import math
import re
import operator
import numpy
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set, Iterable

logger = logging.getLogger(__name__)


def parse_report(stream: io.TextIOBase) -> Iterable[list[int]]:
    for line in stream:
        yield list(map(int, line.split()))


def predict_next(line: list[int]) -> int:
    diff_stack = [numpy.array(line)]
    while True:
        line = diff_stack[0]
        differences = line[1:] - line[:-1]
        if numpy.all(differences == 0):
            break
        diff_stack.insert(0, differences)
    value = 0
    for line in diff_stack:
        value = line[-1] + value
    return value


def part_one():
    report = parse_report(sys.stdin)
    next_values = []
    for line in report:
        next_value = predict_next(line)
        next_values.append(next_value)
    print(sum(next_values))


def part_two():
    report = parse_report(sys.stdin)
    next_values = []
    for line in report:
        next_value = predict_next(line[::-1])
        next_values.append(next_value)
    print(sum(next_values))


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
