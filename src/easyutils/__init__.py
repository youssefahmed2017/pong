"""EasyUtils: simple, readable helpers for everyday Python.

Import the module you need and give it a short name:

    from easyutils import forloop as fl

    for _ in fl.every_hour():
        print("Another hour went by!")

Modules:
    forloop   loops that read like English (every_hour, times, countdown, ...)
    loopvars  helpers for values you track inside loops (Counter, Total, Seen, LoopTimer)
    wait      pausing and timing (seconds, until, stopwatch)
    ask       asking the user for input, with automatic re-asking on bad answers
    say       pretty printing (success, error, box, table, spinner)
    files     one-line file reading and writing (read, write, read_json, read_csv, ...)
    safe      error handling without try/except (retry, timeout, run)
    rand      randomness made simple (coin_flip, dice, pick, password, chance)
"""

from . import ask, files, forloop, loopvars, rand, safe, say, wait

__version__ = "0.2.0"

__all__ = [
    "ask",
    "files",
    "forloop",
    "loopvars",
    "rand",
    "safe",
    "say",
    "wait",
    "__version__",
]
