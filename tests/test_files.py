import pytest

from easyutils import files as ef


def test_write_read_append(tmp_path):
    path = tmp_path / "sub" / "notes.txt"
    ef.write(path, "Hello")
    ef.append(path, "\nWorld")
    assert ef.read(path) == "Hello\nWorld"
    assert list(ef.lines(path)) == ["Hello", "World"]


def test_json_round_trip(tmp_path):
    path = tmp_path / "save.json"
    data = {"level": 3, "name": "يوسف", "items": [1, 2]}
    ef.write_json(path, data)
    assert ef.read_json(path) == data
    assert "يوسف" in ef.read(path)


def test_bad_json_message(tmp_path):
    path = tmp_path / "bad.json"
    ef.write(path, "{oops")
    with pytest.raises(ValueError, match="not valid JSON"):
        ef.read_json(path)


def test_missing_file_message(tmp_path):
    with pytest.raises(FileNotFoundError, match="There is no file"):
        ef.read(tmp_path / "nope.txt")


def test_exists_and_delete(tmp_path):
    path = tmp_path / "x.txt"
    assert not ef.exists(path)
    ef.write(path, "x")
    assert ef.exists(path)
    assert ef.delete(path) is True
    assert ef.delete(path) is False
    with pytest.raises(IsADirectoryError):
        ef.delete(tmp_path)


def test_list_files(tmp_path):
    ef.write(tmp_path / "b.txt", "")
    ef.write(tmp_path / "a.txt", "")
    ef.write(tmp_path / "c.py", "")
    ef.write(tmp_path / "deep" / "d.txt", "")
    names = [p.replace(str(tmp_path), "").lstrip("/\\") for p in ef.list_files(tmp_path, "*.txt")]
    assert names == ["a.txt", "b.txt"]
    assert len(ef.list_files(tmp_path, "**/*.txt")) == 3
    with pytest.raises(NotADirectoryError):
        ef.list_files(tmp_path / "missing")
