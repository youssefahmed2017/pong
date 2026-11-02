import pytest

from easyutils import ask


def test_text(answers, capsys):
    answers("", "  Youssef  ")
    assert ask.text("Name? ") == "Youssef"
    assert "Please type something" in capsys.readouterr().out


def test_text_allow_empty(answers):
    answers("")
    assert ask.text(allow_empty=True) == ""


def test_number_types(answers):
    answers("7", "7.5")
    first, second = ask.number(), ask.number()
    assert first == 7 and isinstance(first, int)
    assert second == 7.5 and isinstance(second, float)


def test_number_reasks_on_bad_input(answers, capsys):
    answers("abc", "3.5", "-1", "200", "42")
    assert ask.number(whole=True, min=0, max=120) == 42
    out = capsys.readouterr().out
    assert "'abc' is not a number" in out
    assert "whole number" in out
    assert "at least 0" in out
    assert "at most 120" in out


@pytest.mark.parametrize("reply,expected", [("y", True), ("YES", True), ("n", False), ("No", False)])
def test_yes_no(answers, reply, expected):
    answers(reply)
    assert ask.yes_no("Continue?") is expected


def test_yes_no_default_and_reask(answers, capsys):
    answers("")
    assert ask.yes_no("Continue?", default=True) is True
    answers("maybe", "", "n")
    assert ask.yes_no("Continue?") is False
    assert "yes or no" in capsys.readouterr().out


def test_choice_by_number_or_text(answers, capsys):
    answers("2")
    assert ask.choice("Pick:", ["red", "blue"]) == "blue"
    answers("9", "RED")
    assert ask.choice("Pick:", ["red", "blue"]) == "red"
    out = capsys.readouterr().out
    assert "1. red" in out and "2. blue" in out
    assert "number from 1 to 2" in out


def test_choice_needs_options():
    with pytest.raises(ValueError):
        ask.choice("Pick:", [])


@pytest.fixture
def secret_answers(monkeypatch):
    def feed(*replies):
        queue = list(replies)
        monkeypatch.setattr("getpass.getpass", lambda prompt="": queue.pop(0))

    return feed


def test_password(secret_answers):
    secret_answers("hunter2")
    assert ask.password() == "hunter2"


def test_password_rules_and_confirm(secret_answers, capsys):
    secret_answers("", "short", "longenough", "different", "longenough", "longenough")
    assert ask.password(confirm=True, min_length=8) == "longenough"
    out = capsys.readouterr().out
    assert "Please type a password" in out
    assert "at least 8 characters" in out
    assert "didn't match" in out
