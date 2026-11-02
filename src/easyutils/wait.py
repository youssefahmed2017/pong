"""Pausing and timing.

    from easyutils import wait as w

    w.seconds(5)
    w.until("17:30")
    w.until(lambda: os.path.exists("done.txt"), check_every=5)

    with w.stopwatch() as sw:
        do_work()
    print(sw.elapsed)
"""

from __future__ import annotations

import datetime as _dt
from typing import Callable, Optional, Union

from . import _clock

__all__ = ["seconds", "minutes", "hours", "until", "stopwatch", "Stopwatch"]


def seconds(n: float) -> None:
    """Pause for `n` seconds."""
    _clock.sleep(_clock.to_seconds(seconds=n))


def minutes(n: float) -> None:
    """Pause for `n` minutes."""
    _clock.sleep(_clock.to_seconds(minutes=n))


def hours(n: float) -> None:
    """Pause for `n` hours."""
    _clock.sleep(_clock.to_seconds(hours=n))


def until(
    target: Union[str, _dt.time, _dt.datetime, Callable[[], bool]],
    check_every: float = 1,
    timeout: Optional[float] = None,
) -> bool:
    """Pause until a clock time, a date and time, or a condition becomes true.

        w.until("09:00")                       # next time the clock shows 09:00
        w.until(datetime(2030, 1, 1))          # a specific moment
        w.until(lambda: job.done, check_every=2, timeout=60)

    For a condition, it's checked every `check_every` seconds. Returns True
    when the wait finished, or False if `timeout` seconds ran out first.
    """
    if callable(target):
        if check_every <= 0:
            raise ValueError("check_every must be more than 0 seconds.")
        deadline = None if timeout is None else _clock.monotonic() + timeout
        while not target():
            if deadline is not None:
                remaining = deadline - _clock.monotonic()
                if remaining <= 0:
                    return False
                _clock.sleep(min(check_every, remaining))
            else:
                _clock.sleep(check_every)
        return True

    if isinstance(target, _dt.datetime):
        moment = target
    else:
        moment = _clock.next_occurrence(_clock.parse_time(target))

    if timeout is not None:
        wait_for = (moment - _clock.now()).total_seconds()
        if wait_for > timeout:
            _clock.sleep(timeout)
            return False
    _clock.sleep_until(moment)
    return True


class Stopwatch:
    """Measures elapsed time. Use it with `with`, or call start() and stop().

        sw = w.Stopwatch().start()
        ...
        sw.stop()
        print(f"{sw.elapsed:.2f} seconds")
    """

    def __init__(self) -> None:
        self._started: Optional[float] = None
        self._stopped: Optional[float] = None

    def start(self) -> "Stopwatch":
        """Start (or restart) timing. Returns the stopwatch itself."""
        self._started = _clock.monotonic()
        self._stopped = None
        return self

    def stop(self) -> float:
        """Stop timing and return the elapsed seconds."""
        if self._started is None:
            raise RuntimeError("The stopwatch was never started. Call start() first.")
        self._stopped = _clock.monotonic()
        return self.elapsed

    @property
    def elapsed(self) -> float:
        """Seconds since start(). Keeps growing until stop() is called."""
        if self._started is None:
            return 0.0
        end = self._stopped if self._stopped is not None else _clock.monotonic()
        return end - self._started

    @property
    def running(self) -> bool:
        """True while the stopwatch is timing."""
        return self._started is not None and self._stopped is None

    def __enter__(self) -> "Stopwatch":
        return self.start()

    def __exit__(self, *exc_info) -> None:
        self.stop()

    def __repr__(self) -> str:
        state = "running" if self.running else "stopped"
        return f"Stopwatch({self.elapsed:.3f}s, {state})"


def stopwatch() -> Stopwatch:
    """Make a stopwatch for a `with` block.

        with w.stopwatch() as sw:
            do_work()
        print(f"That took {sw.elapsed:.1f} seconds")
    """
    return Stopwatch()
