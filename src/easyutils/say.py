"""Pretty printing for the terminal.

    from easyutils import say

    say.success("Saved!")
    say.error("Could not connect")
    say.box("Welcome to my game")
    say.table([{"name": "Ann", "score": 12}, {"name": "Bob", "score": 9}])

    with say.spinner("Downloading"):
        download_everything()

Colors are only used when printing to a real terminal. Set the NO_COLOR
environment variable to turn them off, or FORCE_COLOR to always use them.
"""

from __future__ import annotations

import os
import sys
import threading
from typing import Any, List, Mapping, Optional, Sequence, Union

__all__ = ["success", "error", "warning", "info", "box", "table", "spinner", "Spinner"]

_RESET = "\033[0m"
_COLORS = {
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
}
_windows_ready = False


def _use_color(stream) -> bool:
    global _windows_ready
    if os.environ.get("NO_COLOR"):
        return False
    if not os.environ.get("FORCE_COLOR"):
        isatty = getattr(stream, "isatty", None)
        if not (isatty and isatty()):
            return False
    if os.name == "nt" and not _windows_ready:
        os.system("")  # switches on color support in older Windows consoles
        _windows_ready = True
    return True


def _paint(text: str, color: str, stream) -> str:
    if _use_color(stream):
        return f"{_COLORS[color]}{text}{_RESET}"
    return text


def _status(symbol: str, color: str, message: Any) -> None:
    out = sys.stdout
    print(_paint(f"{symbol} {message}", color, out), file=out)


def success(message: Any) -> None:
    """Print a green success message:  ✔ message"""
    _status("✔", "green", message)


def error(message: Any) -> None:
    """Print a red error message:  ✘ message"""
    _status("✘", "red", message)


def warning(message: Any) -> None:
    """Print a yellow warning message:  ! message"""
    _status("!", "yellow", message)


def info(message: Any) -> None:
    """Print a blue info message:  i message"""
    _status("i", "blue", message)


def box(text: Any, padding: int = 1) -> None:
    """Print text inside a box. Works with several lines too.

        ┌───────┐
        │ Hello │
        └───────┘
    """
    lines = str(text).splitlines() or [""]
    inner = max(len(line) for line in lines) + padding * 2
    pad = " " * padding
    print("┌" + "─" * inner + "┐")
    for line in lines:
        print("│" + pad + line.ljust(inner - padding * 2) + pad + "│")
    print("└" + "─" * inner + "┘")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def table(
    rows: Sequence[Union[Sequence[Any], Mapping[str, Any]]],
    headers: Optional[Sequence[Any]] = None,
) -> None:
    """Print rows as a neat table. Numbers are lined up on the right.

    Rows can be lists:
        say.table([["Ann", 12], ["Bob", 9]], headers=["name", "score"])
    or dicts (the keys become the headers):
        say.table([{"name": "Ann", "score": 12}, {"name": "Bob", "score": 9}])
    """
    if not rows and not headers:
        print("(empty table)")
        return

    raw_rows: List[List[Any]]
    if rows and isinstance(rows[0], Mapping):
        if headers is None:
            headers = []
            for row in rows:
                for key in row:  # type: ignore[union-attr]
                    if key not in headers:
                        headers.append(key)  # type: ignore[union-attr]
        raw_rows = [[row.get(h, "") for h in headers] for row in rows]  # type: ignore[union-attr]
    else:
        raw_rows = [list(row) for row in rows]  # type: ignore[arg-type]

    columns = max([len(headers or [])] + [len(row) for row in raw_rows])
    raw_rows = [row + [""] * (columns - len(row)) for row in raw_rows]
    header_cells = [str(h) for h in headers] + [""] * (columns - len(headers)) if headers else None

    text_rows = [[str(cell) for cell in row] for row in raw_rows]
    widths = [0] * columns
    for row in text_rows + ([header_cells] if header_cells else []):
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(cells: List[str], numeric: List[bool]) -> str:
        parts = [
            cell.rjust(widths[i]) if numeric[i] else cell.ljust(widths[i])
            for i, cell in enumerate(cells)
        ]
        return " | ".join(parts).rstrip()

    if header_cells:
        print(line(header_cells, [False] * columns))
        print("-+-".join("-" * w for w in widths))
    for raw, text_row in zip(raw_rows, text_rows):
        print(line(text_row, [_is_number(cell) for cell in raw]))


class Spinner:
    """A spinning animation that shows something is happening.

        with say.spinner("Downloading"):
            download_everything()

    While the block runs:   ⠹ Downloading
    When it finishes:       ✔ Downloading
    If an error happens:    ✘ Downloading   (and the error carries on as normal)

    Change the text while it spins with `spin.text = "..."`. When the output
    isn't a terminal (for example a log file), only the final line is printed.
    """

    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, text: str = "Working", interval: float = 0.1) -> None:
        self.text = text
        self.interval = interval
        self._stream = sys.stdout
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._width = 0

    def _write(self, line: str) -> None:
        padding = " " * max(0, self._width - len(line))
        self._stream.write("\r" + line + padding)
        self._stream.flush()
        self._width = len(line)

    def _animate(self) -> None:
        frame = 0
        while not self._stop.is_set():
            self._write(f"{self.FRAMES[frame % len(self.FRAMES)]} {self.text}")
            frame += 1
            self._stop.wait(self.interval)

    def start(self) -> "Spinner":
        """Start spinning. Returns the spinner itself."""
        self._stream = sys.stdout
        isatty = getattr(self._stream, "isatty", None)
        if self._thread is None and isatty and isatty():
            self._stop.clear()
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
        return self

    def stop(self, ok: bool = True) -> None:
        """Stop spinning and print the final ✔ (ok) or ✘ (not ok) line."""
        if self._thread is not None:
            self._stop.set()
            self._thread.join()
            self._thread = None
        symbol, color = ("✔", "green") if ok else ("✘", "red")
        if self._width:
            self._write(_paint(f"{symbol} {self.text}", color, self._stream))
            self._stream.write("\n")
            self._width = 0
        else:
            print(_paint(f"{symbol} {self.text}", color, self._stream), file=self._stream)
        self._stream.flush()

    def __enter__(self) -> "Spinner":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop(ok=exc_type is None)


def spinner(text: str = "Working") -> Spinner:
    """Show a spinner while a `with` block runs. See Spinner for details."""
    return Spinner(text)
