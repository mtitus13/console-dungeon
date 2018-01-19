from typing import TypeVar, List
import random


def rand(x: int) -> int:
    return random.randint(0, x - 1)


T = TypeVar("T")


def pick(l: List[T]) -> T:
    return l[rand(len(l))]

