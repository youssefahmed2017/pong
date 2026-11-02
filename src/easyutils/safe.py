"""Error handling without writing try/except yourself.

    from easyutils import safe

    @safe.retry(times=3, delay=2)
    def download():
        ...

    @safe.timeout(seconds=5)
    def slow_thing():
        ...

    value = safe.run(int, "not a number", default=0)   # 0 instead of a crash
"""

from __future__ import annotations

import functools
import threading
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

from . import _clock

__all__ = ["retry", "timeout", "run"]

F = TypeVar("F", bound=Callable[..., Any])
ExceptionTypes = Union[Type[BaseException], Tuple[Type[BaseException], ...]]


def retry(
    times: Union[int, F] = 3,
    *,
    delay: float = 0,
    exceptions: ExceptionTypes = Exception,
):
    """Try a function again if it raises an error.

        @safe.retry                       # up to 3 tries
        @safe.retry(times=5, delay=1)     # up to 5 tries, 1 second apart

    If every try fails, the last error is raised as normal.
    Use `exceptions` to only retry certain errors, e.g. exceptions=ConnectionError.
    """
    if callable(times):  # used as @safe.retry without brackets
        return retry()(times)
    if not isinstance(times, int) or times < 1:
        raise ValueError(f"retry() needs times to be 1 or more, got {times!r}.")
    if delay < 0:
        raise ValueError("retry() delay can't be negative.")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    _clock.sleep(delay)

        return wrapper  # type: ignore[return-value]

    return decorator


def timeout(seconds: float):
    """Give up on a function call that takes longer than `seconds`.

        @safe.timeout(seconds=5)
        def fetch():
            ...

    Raises TimeoutError if the time runs out. Note: Python can't force-stop
    the function, so it keeps running in the background; you just stop
    waiting for it.
    """
    if callable(seconds):
        raise TypeError("Use timeout with a number of seconds, like @safe.timeout(seconds=5).")
    if seconds <= 0:
        raise ValueError("timeout() needs more than 0 seconds.")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            outcome: dict = {}

            def target() -> None:
                try:
                    outcome["value"] = func(*args, **kwargs)
                except BaseException as e:  # passed back to the caller below
                    outcome["error"] = e

            worker = threading.Thread(target=target, daemon=True)
            worker.start()
            worker.join(seconds)
            if worker.is_alive():
                raise TimeoutError(f"{func.__name__}() took longer than {seconds} seconds.")
            if "error" in outcome:
                raise outcome["error"]
            return outcome.get("value")

        return wrapper  # type: ignore[return-value]

    return decorator


def run(func: Callable[..., Any], *args: Any, default: Optional[Any] = None, **kwargs: Any) -> Any:
    """Call `func(*args, **kwargs)`; if it raises an error, return `default` instead.

        safe.run(int, "42")                  # 42
        safe.run(int, "oops", default=0)     # 0
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return default
