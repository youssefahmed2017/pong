from easyutils import say


def test_status_messages_without_color(capsys, monkeypatch):
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    say.success("Saved")
    say.error("Oops")
    say.warning("Careful")
    say.info("FYI")
    assert capsys.readouterr().out == "✔ Saved\n✘ Oops\n! Careful\ni FYI\n"


def test_force_color(capsys, monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    say.success("ok")
    assert capsys.readouterr().out == "\033[32m✔ ok\033[0m\n"


def test_no_color_wins(capsys, monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.setenv("NO_COLOR", "1")
    say.error("x")
    assert capsys.readouterr().out == "✘ x\n"


def test_box(capsys):
    say.box("Hi\nThere")
    assert capsys.readouterr().out == (
        "┌───────┐\n"
        "│ Hi    │\n"
        "│ There │\n"
        "└───────┘\n"
    )


def test_table_from_lists(capsys):
    say.table([["Ann", 12], ["Bob", 9]], headers=["name", "score"])
    assert capsys.readouterr().out == (
        "name | score\n"
        "-----+------\n"
        "Ann  |    12\n"
        "Bob  |     9\n"
    )


def test_table_from_dicts_with_missing_keys(capsys):
    say.table([{"name": "Ann", "score": 12}, {"name": "Bob", "city": "Cairo"}])
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "name | score | city"
    assert lines[3] == "Bob  |       | Cairo"


def test_empty_table(capsys):
    say.table([])
    assert capsys.readouterr().out == "(empty table)\n"


import io
import time

import pytest


def test_spinner_not_a_terminal_prints_final_line(capsys, monkeypatch):
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    with say.spinner("Downloading") as spin:
        spin.text = "Downloaded"
    assert capsys.readouterr().out == "✔ Downloaded\n"


def test_spinner_marks_errors_and_lets_them_through(capsys, monkeypatch):
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    with pytest.raises(KeyError):
        with say.spinner("Saving"):
            raise KeyError("x")
    assert capsys.readouterr().out == "✘ Saving\n"


class FakeTerminal(io.StringIO):
    def isatty(self):
        return True


def test_spinner_animates_in_a_terminal(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    term = FakeTerminal()
    monkeypatch.setattr("sys.stdout", term)
    spin = say.Spinner("Thinking", interval=0.01).start()
    time.sleep(0.05)
    spin.stop()
    out = term.getvalue()
    assert "⠋ Thinking" in out
    assert out.endswith("\r✔ Thinking\n")
