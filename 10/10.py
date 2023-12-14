import logging
import io
import itertools
import enum
import sys
import numpy.typing
from functools import cached_property

logger = logging.getLogger(__name__)


Maze = numpy.typing.NDArray[numpy.char]
Location = tuple[int, ...]


class Direction(enum.Enum):
    up = [-1, 0]
    down = [1, 0]
    left = [0, -1]
    right = [0, 1]

    def step(self, location: Location) -> Location:
        return tuple(numpy.array(location) + self.value)

    @cached_property
    def flipped(self) -> "Direction":
        return {
            Direction.up: Direction.down,
            Direction.down: Direction.up,
            Direction.left: Direction.right,
            Direction.right: Direction.left,
        }[self]


transitions = {
    '-': {Direction.left, Direction.right},
    '|': {Direction.up, Direction.down},
    'J': {Direction.up, Direction.left},
    'L': {Direction.up, Direction.right},
    '7': {Direction.down, Direction.left},
    'F': {Direction.down, Direction.right},
}

transitions_from_next = {
    key: {d1.flipped: d2, d2.flipped: d1}
    for key, (d1, d2) in transitions.items()
}


def parse_maze(stream: io.TextIOBase) -> Maze:
    maze: Maze = numpy.array([list(line.strip()) for line in stream])
    return maze


def find_start(maze: Maze) -> Location:
    return tuple(numpy.argwhere(maze == 'S')[0])


def classify_start(maze: Maze, start: Location) -> str:
    valid_directions = set()
    if start[0] != 0:
        if maze[Direction.up.step(start)] in {'|', 'F', '7'}:
            valid_directions.add(Direction.up)
    if start[1] != 0:
        if maze[Direction.left.step(start)] in {'-', 'F', 'L'}:
            valid_directions.add(Direction.left)
    if start[0] != maze.shape[0]:
        if maze[Direction.down.step(start)] in {'|', 'J', 'L'}:
            valid_directions.add(Direction.down)
    if start[1] != maze.shape[1]:
        if maze[Direction.right.step(start)] in {'-', 'J', '7'}:
            valid_directions.add(Direction.right)
    return next(
        tile for tile, tile_dirs in transitions.items()
        if tile_dirs == valid_directions
    )


def part_one():
    maze = parse_maze(sys.stdin)
    start = find_start(maze)
    start_tile = classify_start(maze, start)
    maze[start] = start_tile

    loop_walker = step_loop(maze, start)
    loop_cells = [start] + list(itertools.takewhile(lambda x: x != start, loop_walker))
    assert len(loop_cells) % 2 == 0
    print(len(loop_cells) // 2)


def step_loop(maze: Maze, start: Location) -> Location:
    location = start
    # Pick an arbitrary start direction from the available directions
    direction = next(iter(transitions[maze[start]]))

    while True:
        location = direction.step(location)
        yield location
        if maze[location] == 'S':
            break
        direction = transitions_from_next[maze[location]][direction]


def part_two():
    maze = parse_maze(sys.stdin)
    start = find_start(maze)
    start_tile = classify_start(maze, start)
    maze[start] = start_tile

    loop_walker = step_loop(maze, start)
    loop_cells = numpy.array([start] + list(
        itertools.takewhile(lambda x: x != start, loop_walker)
    ))

    transitions = numpy.zeros(maze.shape, dtype=int)
    transition_indices = numpy.array([c for c in loop_cells if maze[*c] in '|F7'])
    print(transition_indices)
    transitions[*transition_indices.T] = 1
    print(transitions)

    transition_count = numpy.cumsum(transitions, axis=1)
    transition_count[*loop_cells.T] = 0
    print(transition_count)
    print(numpy.count_nonzero(transition_count % 2 == 1))


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
