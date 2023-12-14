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


def part_one():
    pass



def part_two():
    pass


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
