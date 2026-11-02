"""One-line file reading and writing.

    from easyutils import files as ef

    ef.write("notes.txt", "Hello!")
    text = ef.read("notes.txt")

    ef.write_json("save.json", {"level": 3, "coins": 120})
    data = ef.read_json("save.json")

    for line in ef.lines("big_log.txt"):
        ...

    ef.write_csv("scores.csv", [{"name": "Ann", "score": 12}])
    rows = ef.read_csv("scores.csv")   # [{"name": "Ann", "score": "12"}]

Text is read and written as UTF-8. Folders are created for you when writing.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Optional, Sequence, Union

__all__ = [
    "read",
    "write",
    "append",
    "read_json",
    "write_json",
    "read_csv",
    "write_csv",
    "append_csv",
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


def read_csv(path: PathLike, header: bool = True) -> List[Any]:
    """Read a CSV file.

    With header=True (the default) the first row holds the column names and
    you get a list of dicts:  [{"name": "Ann", "score": "12"}, ...]
    With header=False you get a list of lists:  [["Ann", "12"], ...]

    Every value comes back as text; use int() or float() to turn it into a number.
    """
    p = _file_must_exist(path)
    with p.open(encoding="utf-8-sig", newline="") as f:
        if header:
            return [dict(row) for row in csv.DictReader(f)]
        return [row for row in csv.reader(f)]


def _csv_rows(rows: Sequence[Any], headers: Optional[Sequence[str]]):
    """Split rows (dicts or lists) into a header list and a list of plain rows."""
    if rows and isinstance(rows[0], Mapping):
        if headers is None:
            headers = []
            for row in rows:
                for key in row:
                    if key not in headers:
                        headers.append(key)
        return list(headers), [[row.get(h, "") for h in headers] for row in rows]
    return (list(headers) if headers is not None else None), [list(row) for row in rows]


def write_csv(path: PathLike, rows: Sequence[Any], headers: Optional[Sequence[str]] = None) -> None:
    """Save rows to a CSV file, replacing what was there.

        ef.write_csv("scores.csv", [{"name": "Ann", "score": 12}])          # dicts
        ef.write_csv("scores.csv", [["Ann", 12]], headers=["name", "score"])  # lists
    """
    head, body = _csv_rows(rows, headers)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if head is not None:
            writer.writerow(head)
        writer.writerows(body)


def append_csv(path: PathLike, row: Union[Sequence[Any], Mapping[str, Any]]) -> None:
    """Add one row to the end of a CSV file.

    For a dict row, the columns are matched to the file's header row. If the
    file doesn't exist yet, it's created with the dict's keys as the header.
    """
    p = Path(path)
    if isinstance(row, Mapping):
        if p.exists() and p.stat().st_size > 0:
            with p.open(encoding="utf-8-sig", newline="") as f:
                head = next(csv.reader(f), [])
            unknown = [key for key in row if key not in head]
            if unknown:
                raise ValueError(f"'{path}' has no column called {unknown[0]!r}. Columns: {head}.")
            values = [row.get(h, "") for h in head]
        else:
            write_csv(p, [row])
            return
    else:
        values = list(row)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(values)


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
