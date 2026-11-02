import datetime as dt

import pytest

from easyutils import _clock


class FakeClock:
    """Stands in for the real clock: sleeping just moves time forward."""

    def __init__(self):
        self.mono = 1000.0
        self.wall = dt.datetime(2026, 1, 1, 8, 0, 0)
        self.sleeps = []

    def now(self):
        return self.wall

    def monotonic(self):
        return self.mono

    def sleep(self, seconds):
        if seconds > 0:
            self.sleeps.append(seconds)
            self.advance(seconds)

    def advance(self, seconds):
        """Pretend some work took `seconds`."""
        self.mono += seconds
        self.wall += dt.timedelta(seconds=seconds)


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(_clock, "now", fake.now)
    monkeypatch.setattr(_clock, "monotonic", fake.monotonic)
    monkeypatch.setattr(_clock, "sleep", fake.sleep)
    return fake


@pytest.fixture
def answers(monkeypatch):
    """Feed fake typed answers to input()."""

    def feed(*replies):
        queue = list(replies)
        monkeypatch.setattr("builtins.input", lambda prompt="": queue.pop(0))

    return feed
