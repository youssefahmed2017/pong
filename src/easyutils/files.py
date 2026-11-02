"""One-line file reading and writing.

    from easyutils import files as ef

    ef.write("notes.txt", "Hello!")
    text = ef.read("notes.txt")

    ef.write_json("save.json", {"level": 3, "coins": 120})
    data = ef.read_json("save.json")

    for line in ef.lines("big_log.txt"):
        ...

Text is read and written as UTF-8. Folders are created for you when writing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, List, Union

__all__ = [
    "read",
    "write",
    "append",
    "read_json",
    "write_json",
    "lines",
    "exists",
    "delete",
    "list_files",
]

PathLike = Union[str, Path]


def _file_must_exist(path: PathLike) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"There is no file called '{path}'.")
    if p.is_dir():
        raise IsADirectoryError(f"'{path}' is a folder, not a file.")
    return p


def read(path: PathLike) -> str:
    """Read a whole text file and return its contents."""
    return _file_must_exist(path).read_text(encoding="utf-8")


def write(path: PathLike, text: Any) -> None:
    """Write text to a file, replacing what was there. Creates folders if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(text), encoding="utf-8")


def append(path: PathLike, text: Any) -> None:
    """Add text to the end of a file. Creates the file (and folders) if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(str(text))


def read_json(path: PathLike) -> Any:
    """Read a JSON file and return the data (usually a dict or list)."""
    p = _file_must_exist(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"'{path}' is not valid JSON (line {e.lineno}: {e.msg}).") from None


def write_json(path: PathLike, data: Any, indent: int = 2) -> None:
    """Save data (dicts, lists, strings, numbers...) to a JSON file."""
    write(path, json.dumps(data, indent=indent, ensure_ascii=False))


def lines(path: PathLike) -> Iterator[str]:
    """Loop over a file one line at a time, without the newline at the end.

    Works on huge files too, because it doesn't load the whole file at once.
    """
    p = _file_must_exist(path)
    with p.open(encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\r\n")


def exists(path: PathLike) -> bool:
    """True if a file or folder exists at `path`."""
    return Path(path).exists()


def delete(path: PathLike) -> bool:
    """Delete a file. Returns True if it was deleted, False if it wasn't there."""
    p = Path(path)
    if p.is_dir():
        raise IsADirectoryError(f"'{path}' is a folder. delete() only removes files.")
    if not p.exists():
        return False
    p.unlink()
    return True


def list_files(folder: PathLike = ".", pattern: str = "*") -> List[str]:
    """List the files in a folder, sorted by name.

        ef.list_files("photos", "*.jpg")
        ef.list_files("project", "**/*.py")   # ** looks inside subfolders too
    """
    base = Path(folder)
    if not base.is_dir():
        raise NotADirectoryError(f"There is no folder called '{folder}'.")
    return sorted(str(p) for p in base.glob(pattern) if p.is_file())
