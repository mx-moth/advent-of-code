import logging
import itertools
import math
import io
import re
import sys
from typing import Tuple, List, Dict, Iterable

logger = logging.getLogger(__name__)


NODE_RE = re.compile('([A-Z0-9]+) = \(([A-Z0-9]+), ([A-Z0-9]+)\)')

def parse_map(
    stream: io.TextIOBase,
) -> tuple[
    list[int], dict[str, tuple[str, str]]
]:
    turns_line = stream.readline().strip()
    turns = list(map(
        {'L': 0, 'R': 1}.__getitem__,
        turns_line
    ))
    stream.readline()

    nodes = {}
    for line in stream:
        node_match = NODE_RE.match(line)
        nodes[node_match[1]] = (node_match[2], node_match[3])

    return turns, nodes


def navigate(
    start: str,
    turns: list[int],
    nodes: dict[str, tuple[str, str]]
) -> Iterable[str]:
    node = start
    for turn in itertools.cycle(turns):
        node = nodes[node][turn]
        yield node


def part_one():
    turns, nodes = parse_map(sys.stdin)
    step, node = next(
        (step, node)
        for step, node in enumerate(navigate('AAA', turns, nodes), start=1)
        if node == 'ZZZ'
    )
    print(step)


def part_two():
    turns, nodes = parse_map(sys.stdin)
    starts = [node for node in nodes.keys() if node.endswith('A')]
    ends = {node for node in nodes.keys() if node.endswith('Z')}
    cycle_lengths = []
    for start in starts:
        steps = next(
            step for step, node in enumerate(navigate(start, turns, nodes), start=1)
            if node in ends and step % len(turns) == 0
        )
        cycle_lengths.append(steps // len(turns))

    print(math.lcm(*cycle_lengths) * len(turns))


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
