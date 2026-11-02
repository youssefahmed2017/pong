"""Randomness made simple.

    from easyutils import rand as r

    r.coin_flip()            # "heads" or "tails"
    r.dice()                 # 1 to 6
    r.pick(["a", "b", "c"])  # one random item
    r.chance(30)             # True 30% of the time
    r.password(length=16)    # a strong random password
"""

from __future__ import annotations

import random
import secrets
import string
from typing import List, Sequence, TypeVar

__all__ = ["coin_flip", "dice", "number", "pick", "pick_many", "shuffle", "chance", "password"]

T = TypeVar("T")


def coin_flip() -> str:
    """Return "heads" or "tails"."""
    return random.choice(["heads", "tails"])


def dice(sides: int = 6) -> int:
    """Roll one die with `sides` sides (6 by default). Returns 1 to sides."""
    if not isinstance(sides, int) or sides < 1:
        raise ValueError(f"A die needs at least 1 side, got {sides!r}.")
    return random.randint(1, sides)


def number(low: int, high: int) -> int:
    """A random whole number from low to high (both included)."""
    if low > high:
        raise ValueError(f"low ({low}) must not be bigger than high ({high}).")
    return random.randint(low, high)


def pick(items: Sequence[T]) -> T:
    """Pick one random item."""
    if not items:
        raise ValueError("Can't pick from an empty list.")
    return random.choice(list(items))


def pick_many(items: Sequence[T], count: int) -> List[T]:
    """Pick `count` different random items."""
    if count > len(items):
        raise ValueError(f"Can't pick {count} items from a list of {len(items)}.")
    return random.sample(list(items), count)


def shuffle(items: Sequence[T]) -> List[T]:
    """Return a shuffled copy of `items`. The original is left unchanged."""
    copy = list(items)
    random.shuffle(copy)
    return copy


def chance(percent: float) -> bool:
    """True `percent`% of the time. chance(25) is True about 1 in 4 times."""
    if not 0 <= percent <= 100:
        raise ValueError(f"chance() needs a percent from 0 to 100, got {percent!r}.")
    return random.random() * 100 < percent


def password(length: int = 12, symbols: bool = True) -> str:
    """Make a strong random password.

    Always includes at least one lowercase letter, uppercase letter and digit
    (and one symbol when symbols=True). Uses the `secrets` module, which is
    safe for real passwords.
    """
    groups = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        groups.append("!@#$%^&*-_=+?")
    if length < len(groups):
        raise ValueError(f"A password needs to be at least {len(groups)} characters long.")
    every_char = "".join(groups)
    chars = [secrets.choice(group) for group in groups]
    chars += [secrets.choice(every_char) for _ in range(length - len(groups))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
