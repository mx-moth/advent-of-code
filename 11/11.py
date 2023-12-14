import logging
import io
import numpy
import sys

logger = logging.getLogger(__name__)


def parse_galaxy(stream: io.TextIOBase) -> numpy.ndarray:
    return numpy.array(
        [list(line.strip()) for line in stream],
        dtype='S1',
    )


def expand_galaxy(
    galaxy: numpy.ndarray,
    expansion_factor: int = 1,
):
    galaxy_locations = numpy.argwhere(galaxy == b'#')
    empty_space = galaxy == b'.'
    row_expansion = (expansion_factor - 1) * numpy.cumsum(numpy.all(empty_space, axis=0))
    column_expansion = (expansion_factor - 1) * numpy.cumsum(numpy.all(empty_space, axis=1))
    expanded_galaxy_locations = numpy.array([
        [column + column_expansion[column], row + row_expansion[row]]
        for column, row in galaxy_locations
    ])
    return expanded_galaxy_locations



def compute_distances(
    galaxy: numpy.ndarray,
    expansion_factor: int,
) -> numpy.ndarray:
    galaxy_locations = expand_galaxy(galaxy, expansion_factor)
    total_distance = 0
    for source in range(len(galaxy_locations)):
        source_location = galaxy_locations[source]
        dest_locations = galaxy_locations[source + 1:]
        total_distance += numpy.sum(numpy.abs(dest_locations - source_location))
    return total_distance


def part_one():
    galaxy = parse_galaxy(sys.stdin)
    total_distance = compute_distances(galaxy, 2)
    print(total_distance)


def part_two():
    galaxy = parse_galaxy(sys.stdin)
    total_distance = compute_distances(galaxy, 1_000_000)
    print(total_distance)


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
