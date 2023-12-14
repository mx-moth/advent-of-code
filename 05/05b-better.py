import dataclasses
import itertools
import io
import re
import operator
import sys
from functools import reduce
from typing import Optional, Tuple, List, Set, Dict


@dataclasses.dataclass
class Range:
    start: int
    stop: int

    def __contains__(self, value) -> bool:
        return self.start <= value <= self.stop

    def to_offset(self, value: int) -> int:
        return value - self.start

    def from_offset(self, offset: int) -> int:
        return offset + self.start

    @classmethod
    def from_start_length(cls, start: int, length: int):
        return cls(start, start + length - 1)


class RangeMap:
    name: str
    ranges: List[Tuple[Range, Range]]

    def __init__(self, name: str, ranges: List[Tuple[Range, Range]]):
        self.name = name
        self.ranges = ranges

    def __getitem__(self, value: int) -> int:
        for source, dest in self.ranges:
            if value in dest:
                result = source.from_offset(dest.to_offset(value))
                return result
        return value

    def __repr__(self):
        ranges = ', '.join(f'({source} -> {dest})' for source, dest in self.ranges)
        return f'<RangeMap {ranges}>'


SEEDS_RE = re.compile('seeds: ')
MAP_NAME_RE = re.compile(r'(\w+)-to-(\w+) map:')


def parse_almanac(stream: io.TextIOBase) -> Tuple[List[int], Dict[str, RangeMap]]:
    seeds_line = stream.readline()
    match = SEEDS_RE.match(seeds_line)
    seeds = list(map(int, seeds_line[match.end():].split()))
    assert stream.readline() == '\n'

    range_maps = {}
    while (map_name_line := stream.readline()):
        map_name_match = MAP_NAME_RE.match(map_name_line)
        map_name = (map_name_match[1], map_name_match[2])
        ranges = []

        while (range_line := stream.readline()) not in {'', '\n'}:
            dest_start, source_start, length = map(int, range_line.split())
            ranges.append((
                Range.from_start_length(source_start, length),
                Range.from_start_length(dest_start, length),
            ))

        range_maps[map_name] = RangeMap(f'{map_name[0]}-to-{map_name[1]}', ranges)

    return seeds, range_maps


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def grouper(iterable, n):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip(*args)


transitions = [
    'seed', 'soil', 'fertilizer', 'water', 'light',
    'temperature', 'humidity', 'location',
]


def part_two():
    seeds, maps = parse_almanac(sys.stdin)
    seed_ranges = [
        Range.from_start_length(start, length)
        for start, length in grouper(seeds, 2)
    ]
    value = 0
    maps_in_order = [
        maps[transition] for transition in pairwise(transitions)
    ]
    maps_in_order = maps_in_order[::-1]
    while True:
        if value % 1000 == 0:
            print("Trying location", value)
        result = reduce(lambda v, m: m[v], maps_in_order, value)
        if any(result in seed_range for seed_range in seed_ranges):
            print(value)
            break
        value += 1


part_two()
