"""Helpers for the values you keep track of inside loops.

    from easyutils import loopvars as lv

    total = lv.Total()
    for price in prices:
        total.add(price)
    print(total.sum, total.average, total.max)
"""

from __future__ import annotations

from typing import Hashable, Optional, Set

from . import _clock

__all__ = ["Counter", "Total", "Seen", "LoopTimer"]


class Counter:
    """A number you can count up and down.

        c = lv.Counter()
        c.up()          # 1
        c.up(by=5)      # 6
        c.down()        # 5
        c.reset()       # 0
    """

    def __init__(self, start: int = 0) -> None:
        self._start = start
        self.value = start

    def up(self, by: int = 1) -> int:
        """Add `by` (default 1) and return the new value."""
        self.value += by
        return self.value

    def down(self, by: int = 1) -> int:
        """Subtract `by` (default 1) and return the new value."""
        self.value -= by
        return self.value

    def reset(self) -> int:
        """Go back to the starting value and return it."""
        self.value = self._start
        return self.value

    def __int__(self) -> int:
        return int(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Counter):
            return self.value == other.value
        return self.value == other

    def __repr__(self) -> str:
        return f"Counter({self.value})"


class Total:
    """Collects numbers and gives you the sum, count, average, min and max.

        t = lv.Total()
        for score in [3, 9, 6]:
            t.add(score)
        t.sum      # 18
        t.average  # 6.0
        t.max      # 9

    average, min and max are None until you add something.
    """

    def __init__(self) -> None:
        self.sum: float = 0
        self.count: int = 0
        self.min: Optional[float] = None
        self.max: Optional[float] = None

    def add(self, number: float) -> None:
        """Add one number."""
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            raise TypeError(f"Total.add() needs a number, got {number!r}.")
        self.sum += number
        self.count += 1
        self.min = number if self.min is None else min(self.min, number)
        self.max = number if self.max is None else max(self.max, number)

    @property
    def average(self) -> Optional[float]:
        """The average of everything added so far, or None if nothing was added."""
        return self.sum / self.count if self.count else None

    def reset(self) -> None:
        """Forget everything and start again."""
        self.__init__()

    def __repr__(self) -> str:
        return f"Total(sum={self.sum}, count={self.count}, average={self.average})"


class Seen:
    """Remembers which things you've already come across.

        seen = lv.Seen()
        for email in emails:
            if seen.first_time(email):
                send_welcome(email)   # each address only once
    """

    def __init__(self) -> None:
        self._items: Set[Hashable] = set()

    def first_time(self, item: Hashable) -> bool:
        """True the first time you pass `item`, False every time after."""
        if item in self._items:
            return False
        self._items.add(item)
        return True

    def add(self, item: Hashable) -> None:
        """Remember `item` without checking it."""
        self._items.add(item)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Seen({len(self._items)} items)"


class LoopTimer:
    """Measures how long each round of a loop takes.

        timer = lv.LoopTimer()
        for file in files:
            process(file)
            print(f"took {timer.tick():.2f}s")
        print(f"average {timer.average:.2f}s")
    """

    def __init__(self) -> None:
        self._last_mark = _clock.monotonic()
        self.last: Optional[float] = None
        self.total: float = 0.0
        self.count: int = 0

    def tick(self) -> float:
        """Mark the end of a round and return how many seconds it took."""
        mark = _clock.monotonic()
        took = mark - self._last_mark
        self._last_mark = mark
        self.last = took
        self.total += took
        self.count += 1
        return took

    @property
    def average(self) -> Optional[float]:
        """Average seconds per round, or None before the first tick()."""
        return self.total / self.count if self.count else None

    def __repr__(self) -> str:
        return f"LoopTimer(count={self.count}, last={self.last}, average={self.average})"
