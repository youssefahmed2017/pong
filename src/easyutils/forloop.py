"""Loops that read like English.

    from easyutils import forloop as fl

    for _ in fl.every_hour():
        check_email()

    for i in fl.countdown(3):
        print(i)          # 3, 2, 1
"""

from __future__ import annotations

import datetime as _dt
import math
import sys
from typing import Iterable, Iterator, List, Optional, Tuple, TypeVar

from . import _clock

T = TypeVar("T")

__all__ = [
    "every",
    "every_second",
    "every_minute",
    "every_hour",
    "every_day",
    "times",
    "forever",
    "for_duration",
    "countdown",
    "with_progress",
    "pairs",
    "chunks",
    "mark_last",
]


def _check_times(times: Optional[int]) -> None:
    if times is not None and (not isinstance(times, int) or times < 0):
        raise ValueError(f"times must be a whole number of 0 or more, got {times!r}.")


# ---------------------------------------------------------------------------
# Timed loops
# ---------------------------------------------------------------------------

def every(
    seconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    *,
    times: Optional[int] = None,
    start_now: bool = True,
) -> Iterator[int]:
    """Loop on a fixed interval, forever or for a set number of `times`.

    Yields the run number (0, 1, 2, ...).

        for run in fl.every(seconds=10):
            print("run number", run)

    With start_now=True (the default) the first run happens straight away.
    With start_now=False the loop waits one interval before the first run.

    The schedule doesn't drift: runs stay on the same rhythm even if the loop
    body takes a moment. If the body takes longer than the interval, the
    missed runs are skipped and the loop waits for the next slot.
    """
    interval = _clock.to_seconds(seconds, minutes, hours)
    if interval <= 0:
        raise ValueError("every() needs a positive interval, for example every(seconds=10).")
    _check_times(times)

    next_run = _clock.monotonic() + (0 if start_now else interval)
    count = 0
    while times is None or count < times:
        _clock.sleep(next_run - _clock.monotonic())
        yield count
        count += 1
        next_run += interval
        late_by = _clock.monotonic() - next_run
        if late_by > 0:
            next_run += math.ceil(late_by / interval) * interval


def every_second(*, times: Optional[int] = None, start_now: bool = True) -> Iterator[int]:
    """Loop once every second. Same as every(seconds=1)."""
    return every(seconds=1, times=times, start_now=start_now)


def every_minute(*, times: Optional[int] = None, start_now: bool = True) -> Iterator[int]:
    """Loop once every minute. Same as every(minutes=1)."""
    return every(minutes=1, times=times, start_now=start_now)


def every_hour(*, times: Optional[int] = None, start_now: bool = True) -> Iterator[int]:
    """Loop once every hour. Same as every(hours=1)."""
    return every(hours=1, times=times, start_now=start_now)


def every_day(at: str = "00:00", *, times: Optional[int] = None) -> Iterator[int]:
    """Loop once a day at a set clock time, like at="09:00" or at="17:30:15".

    Waits for the next time the clock shows `at` before the first run.
    Yields the run number (0, 1, 2, ...).

        for _ in fl.every_day(at="08:00"):
            send_morning_report()
    """
    clock_time = _clock.parse_time(at)
    _check_times(times)

    target = _clock.next_occurrence(clock_time)
    count = 0
    while times is None or count < times:
        _clock.sleep_until(target)
        yield count
        count += 1
        target += _dt.timedelta(days=1)
        while target <= _clock.now():  # the body ran for over a day: skip missed days
            target += _dt.timedelta(days=1)


def for_duration(seconds: float = 0, minutes: float = 0, hours: float = 0) -> Iterator[int]:
    """Keep looping until the given amount of time has passed.

    Yields the run number (0, 1, 2, ...). The loop body is never cut off
    halfway; the time is checked before each new run.

        for _ in fl.for_duration(minutes=2):
            do_some_work()
    """
    duration = _clock.to_seconds(seconds, minutes, hours)
    end = _clock.monotonic() + duration
    count = 0
    while _clock.monotonic() < end:
        yield count
        count += 1


# ---------------------------------------------------------------------------
# Counting loops
# ---------------------------------------------------------------------------

def times(n: int) -> Iterator[int]:
    """Loop exactly `n` times. Yields 0, 1, ..., n-1 (like range(n)).

        for _ in fl.times(3):
            print("hip hip hooray!")
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"times() needs a whole number of 0 or more, got {n!r}.")
    return iter(range(n))


def forever() -> Iterator[int]:
    """Loop forever (until you `break`). Yields 0, 1, 2, ..."""
    count = 0
    while True:
        yield count
        count += 1


def countdown(start: int, stop: int = 1) -> Iterator[int]:
    """Count down from `start` to `stop` (inclusive).

        list(fl.countdown(5))      # [5, 4, 3, 2, 1]
        list(fl.countdown(3, 0))   # [3, 2, 1, 0]
    """
    if not isinstance(start, int) or not isinstance(stop, int):
        raise ValueError("countdown() needs whole numbers, for example countdown(10).")
    return iter(range(start, stop - 1, -1))


# ---------------------------------------------------------------------------
# Loops over your own data
# ---------------------------------------------------------------------------

def with_progress(
    items: Iterable[T],
    label: str = "",
    width: int = 30,
    stream=None,
) -> Iterator[T]:
    """Loop over `items` while showing a progress bar.

        for photo in fl.with_progress(photos, label="Resizing"):
            resize(photo)

    Prints something like:  Resizing [###########-------------------] 12/32
    The bar is written to stderr by default so it doesn't mix with your
    normal print() output.
    """
    out = stream if stream is not None else sys.stderr
    item_list = items if hasattr(items, "__len__") else list(items)
    total = len(item_list)  # type: ignore[arg-type]
    prefix = f"{label} " if label else ""

    def draw(done: int) -> None:
        filled = width if total == 0 else int(width * done / total)
        bar = "#" * filled + "-" * (width - filled)
        out.write(f"\r{prefix}[{bar}] {done}/{total}")
        out.flush()

    draw(0)
    for done, item in enumerate(item_list, start=1):  # type: ignore[arg-type]
        yield item
        draw(done)
    out.write("\n")
    out.flush()


def pairs(items: Iterable[T]) -> Iterator[Tuple[T, T]]:
    """Loop over each item together with the one after it.

        list(fl.pairs([1, 2, 3, 4]))   # [(1, 2), (2, 3), (3, 4)]
    """
    iterator = iter(items)
    try:
        previous = next(iterator)
    except StopIteration:
        return
    for item in iterator:
        yield previous, item
        previous = item


def chunks(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """Loop over `items` in groups of `size`. The last group may be smaller.

        list(fl.chunks([1, 2, 3, 4, 5], size=2))   # [[1, 2], [3, 4], [5]]
    """
    if not isinstance(size, int) or size < 1:
        raise ValueError(f"chunks() needs a size of 1 or more, got {size!r}.")
    group: List[T] = []
    for item in items:
        group.append(item)
        if len(group) == size:
            yield group
            group = []
    if group:
        yield group


def mark_last(items: Iterable[T]) -> Iterator[Tuple[T, bool]]:
    """Loop over `items`, also telling you whether each one is the last.

        for name, is_last in fl.mark_last(["Ann", "Bob", "Cy"]):
            print(name, end="\\n" if is_last else ", ")
    """
    iterator = iter(items)
    try:
        current = next(iterator)
    except StopIteration:
        return
    for item in iterator:
        yield current, False
        current = item
    yield current, True
