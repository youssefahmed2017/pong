import datetime as dt

import pytest

from easyutils import wait as w


def test_simple_waits(clock):
    w.seconds(5)
    w.minutes(2)
    w.hours(1)
    assert clock.sleeps == [5, 120, 3600]


def test_negative_wait_is_an_error(clock):
    with pytest.raises(ValueError):
        w.seconds(-1)


def test_until_clock_time(clock):
    assert w.until("09:15") is True
    assert clock.wall == dt.datetime(2026, 1, 1, 9, 15)


def test_until_datetime(clock):
    w.until(dt.datetime(2026, 1, 3))
    assert clock.wall == dt.datetime(2026, 1, 3)


def test_until_datetime_in_the_past_returns_straight_away(clock):
    assert w.until(dt.datetime(2020, 1, 1)) is True
    assert clock.sleeps == []


def test_until_time_with_timeout(clock):
    assert w.until("10:00", timeout=60) is False
    assert clock.sleeps == [60]


def test_until_condition(clock):
    start = clock.mono
    assert w.until(lambda: clock.mono - start >= 10, check_every=3) is True
    assert clock.mono - start == 12


def test_until_condition_timeout(clock):
    start = clock.mono
    assert w.until(lambda: False, check_every=4, timeout=10) is False
    assert clock.mono - start == 10


def test_stopwatch_with_block(clock):
    with w.stopwatch() as sw:
        clock.advance(7)
        assert sw.running
        assert sw.elapsed == 7
    clock.advance(100)
    assert not sw.running
    assert sw.elapsed == 7


def test_stopwatch_start_stop(clock):
    sw = w.Stopwatch()
    assert sw.elapsed == 0
    with pytest.raises(RuntimeError):
        sw.stop()
    sw.start()
    clock.advance(2.5)
    assert sw.stop() == 2.5
