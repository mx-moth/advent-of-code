import dataclasses
import io
import itertools
import logging
import logging.config
import re
import sys
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)


@dataclasses.dataclass(order=True)
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

    def convert(self, dest: "Range", value: int) -> int:
        """Covert a value from the source range to the dest range."""
        if value not in self:
            raise ValueError(f"Value {value} out of range of source {self}")
        return dest.from_offset(self.to_offset(value))

    def remap(
        self,
        source: "Range",
        dest: "Range",
    ) -> Tuple[List["Range"], List["Range"]]:
        """
        Map any overlaps in this range from `source` to `dest`.
        Returns a tuple of two possibly empty lists of ranges:
        unmapped and remapped ranges in that order.
        """
        if self.start > source.stop or self.stop < source.start:
            # No overlap, return this map unmodified
            return [self], []

        ranges = []
        if source.start <= self.start:
            if source.stop >= self.stop:
                # The source remaps this entire range
                return [], [Range(
                    source.convert(dest, self.start),
                    source.convert(dest, self.stop),
                )]
            else:
                # Overlaps on the left edge
                return [Range(source.stop + 1, self.stop)], [
                    Range(
                        source.convert(dest, self.start),
                        source.convert(dest, source.stop),
                    ),
                ]
        else:
            if source.stop >= self.stop:
                # Overlaps on the right edge
                return [Range(self.start, source.start - 1)], [
                    Range(
                        source.convert(dest, source.start),
                        source.convert(dest, self.stop),
                    ),
                ]
            else:
                # Overlaps just in the middle
                return [
                    Range(self.start, source.start - 1),
                    Range(source.stop + 1, self.stop),
                ], [
                    Range(
                        source.convert(dest, source.start),
                        source.convert(dest, source.stop),
                    ),
                ]
        return ranges

    def __str__(self) -> str:
        return f'[{self.start}, {self.stop}]'


class RangeMap:
    name: str
    ranges: List[Tuple[Range, Range]]

    def __init__(self, name: str, ranges: List[Tuple[Range, Range]]):
        self.name = name
        self.ranges = ranges

    def __str__(self):
        maps = ''.join(f'\n    ({source} -> {dest})' for source, dest in self.ranges)
        return f'{self.name}: [{maps}]'

    def __repr__(self):
        return f'<RangeMap {self}>'


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
    """
    Start with the seeds as the current value ranges.

    For every map, processed in order,
    find overlaps between the value ranges and the source ranges.
    Remap the overlapping sections from source to destination.
    Combine any remaining unmapped value ranges with the remapped value ranges.
    Repeat until all maps have been processed.

    The value ranges are now the location ranges for all seeds.
    Find the minimum starting value for the value ranges for the answer.
    """
    seeds, maps = parse_almanac(sys.stdin)

    # Start with all seed ranges
    value_ranges = [
        Range.from_start_length(start, length)
        for start, length in grouper(seeds, 2)
    ]
    logger.info("Seed ranges: %s", ', '.join(map(str, value_ranges)))

    for transition in pairwise(transitions):
        range_map = maps[transition]
        logger.info("Processing transition %s", range_map.name)
        logger.info("%s", range_map)
        # For each range map, map overlaps with the current unmapped value
        # ranges to destination ranges.
        # Keep separate records of unmapped and remapped ranges to avoid
        # double-processing ranges.
        remapped_ranges = []
        for source, dest in range_map.ranges:
            next_values = []
            for r in value_ranges:
                unmapped_r, remapped_r = r.remap(source, dest)
                next_values.extend(unmapped_r)
                remapped_ranges.extend(remapped_r)
            value_ranges = next_values

        # Combine any remaining unmapped values with the remapped values
        # ready for the next transition
        value_ranges = sorted(value_ranges + remapped_ranges)

    # The ranges are now all location ranges. Find the minimum start value to
    # find the closest location
    min_value = min(value_range.start for value_range in value_ranges)
    print(min_value)


logging.basicConfig(level=logging.WARNING)
part_two()
