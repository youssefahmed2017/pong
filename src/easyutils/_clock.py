"""Internal time helpers shared by the other modules.

Everything that reads the clock or sleeps goes through this module, so the
tests can swap in a fake clock and run instantly.
"""

from __future__ import annotations

import datetime as _dt
import time as _time


def now() -> _dt.datetime:
    """The current wall-clock date and time."""
    return _dt.datetime.now()


def monotonic() -> float:
    """A clock that only moves forward, for measuring durations."""
    return _time.monotonic()


def sleep(seconds: float) -> None:
    """Sleep for `seconds`. Zero or negative values return immediately."""
    if seconds > 0:
        _time.sleep(seconds)


def to_seconds(seconds: float = 0, minutes: float = 0, hours: float = 0, days: float = 0) -> float:
    """Add up a duration given in different units and return it in seconds."""
    total = seconds + minutes * 60 + hours * 3600 + days * 86400
    if total < 0:
        raise ValueError(f"A duration can't be negative (got {total} seconds).")
    return total


def parse_time(value) -> _dt.time:
    """Turn '09:00' or '17:30:15' (or a datetime.time) into a datetime.time."""
    if isinstance(value, _dt.time):
        return value
    message = f"Expected a time like '09:00' or '17:30:15', got {value!r}."
    if not isinstance(value, str):
        raise ValueError(message)
    try:
        parts = [int(part) for part in value.strip().split(":")]
    except ValueError:
        raise ValueError(message) from None
    if len(parts) not in (2, 3):
        raise ValueError(message)
    try:
        return _dt.time(*parts)
    except ValueError:
        raise ValueError(message) from None


def next_occurrence(at: _dt.time) -> _dt.datetime:
    """The next date and time (strictly after now) when the clock shows `at`."""
    current = now()
    target = _dt.datetime.combine(current.date(), at)
    if target <= current:
        target += _dt.timedelta(days=1)
    return target


def sleep_until(target: _dt.datetime) -> None:
    """Sleep until the wall clock reaches `target`."""
    while True:
        remaining = (target - now()).total_seconds()
        if remaining <= 0:
            return
        sleep(remaining)
