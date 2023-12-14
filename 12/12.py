import enum
import functools
import io
import logging
import numpy
import sys
from typing import Iterable, Callable

logger = logging.getLogger(__name__)


class Condition(str, enum.Enum):
    WORKING = '#'
    BROKEN = '.'
    UNKNOWN = '?'

    def __repr__(self):
        return self.value


def parse_report(
    stream: io.TextIOBase,
) -> Iterable[tuple[list[Condition], list[int]]]:
    for line in stream:
        springs, groups = line.split()
        yield (
            list(map(Condition, springs)),
            list(map(int, groups.split(','))),
        )


class memoize:
    def __new__(
        cls,
        fn: Callable | None = None,
        /,
        **kwargs,
    ):
        if fn is None:
            return lambda fn: cls(fn, **kwargs)
        else:
            print("Making regular memoized")
            return super().__new__(cls)

    def __init__(self, fn: Callable, /, *, key: Callable = lambda *a: tuple(a)):
        self.fn = fn
        self.key = key
        self.cache = {}

    def __call__(self, *args):
        key = self.key(*args)
        if key in self.cache:
            return self.cache[key]
        else:
            out = self.fn(*args, self)
            self.cache[key] = out
            return out

    def copy(self):
        return memoize(self.fn, key=self.key)


@memoize(key=lambda cs, gs: (tuple(tuple(c) for c in cs), tuple(gs)))
def test_combinations(
    chunks: list[list[Condition]],
    counts: list[int],
    test_combinations: Callable,
) -> int:

    if len(counts) == 0:
        # No more expected groups!
        if any(Condition.WORKING in chunk for chunk in chunks):
            # There are remaining working springs in the future chunks
            # but we've used up all our expected groups.
            # This is not a working combination.
            return 0

        else:
            # There are no remaining working springs in the remaining groups.
            # Great success, we've found a working combination!
            return 1

    if len(chunks) == 0:
        # There are still expected groups of working springs,
        # but there are no more chunks to fit them in!
        # This is not a working combination.
        return 0

    logger.info("%s %s", chunks, counts)

    chunk = chunks[0]
    count = counts[0]

    logger.info(
        "  Trying to fit %s springs in %s",
        count, chunk)

    working_combinations = 0

    if count < len(chunk):
        chunk_tail = chunk[count:]
        if chunk_tail[0] == Condition.WORKING:
            # Oop, placing the group at the start of the chunk is bad!
            # There is a trailing '#' immediately following
            # it blowing out the size
            pass
        else:
            if len(chunk_tail) > 1:
                # Skip one '?' and place remaining counts in the rest of this chunk
                working_combinations += test_combinations(
                    [chunk_tail[1:]] + chunks[1:], counts[1:])
            else:
                # The chunk tail was a single '?', so skip it
                working_combinations += test_combinations(chunks[1:], counts[1:])

        if chunk[0] == Condition.WORKING:
            # Chunk starts with a working spring, so this group is not movable
            pass
        elif len(chunk) > 1:
            # Try placing this group further along in the chunk
            working_combinations += test_combinations([chunk[1:]] + chunks[1:], counts)

        return working_combinations

    if count == len(chunk):
        # This count matches the chunk size exactly!
        # This is a potentially working combination.
        # Recurse down with the remaining chunks
        working_combinations = test_combinations(chunks[1:], counts[1:])

        if Condition.WORKING not in chunk:
            # The current chunk is entirely skippable
            # Try placing this count in the next chunk also
            working_combinations += test_combinations(
                chunks[1:], counts)

        return working_combinations

    if Condition.WORKING not in chunk:
        # This chunk doesn't fit the current count, but is made up entirely of
        # unknown springs.
        # Assume they are all broken and try from the next chunk.
        return test_combinations(chunks[1:], counts)

    # This chunk is smaller than the expected count
    # but it has a working spring.
    # This is not a working combination.
    return 0


def count_combinations(springs: list[list[Condition]], groups: list[int]):
    chunks = [
        list(map(Condition, chunk))
        for chunk in ''.join(springs).split(Condition.BROKEN)
        if chunk != ''
    ]

    return test_combinations.copy()(chunks, groups)


def part_one():
    total_working_combinations = 0
    for springs, expected_groups in parse_report(sys.stdin):
        logger.debug("--------------")
        logger.info("%s %s", springs, expected_groups)
        working_combinations = count_combinations(springs, expected_groups)
        total_working_combinations += working_combinations
        logger.info("Working combinations: %s", working_combinations)
    print(total_working_combinations)


def part_two():
    total_working_combinations = 0
    # For each line in the report,
    # the actual layout is [springs]?[springs]?[springs]?[springs]?[springs]
    # and the expected count is [count] * 5.
    for springs, expected_groups in parse_report(sys.stdin):
        springs = (springs + [Condition.UNKNOWN]) * 4 + springs
        expected_groups = expected_groups * 5
        logger.debug("--------------")
        logger.info("%s %s", springs, expected_groups)
        working_combinations = count_combinations(springs, expected_groups)
        logger.info("Working combinations: %s", working_combinations)
        total_working_combinations += working_combinations
    print(total_working_combinations)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
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


