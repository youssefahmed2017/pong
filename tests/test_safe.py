import time

import pytest

from easyutils import safe


def make_flaky(fail_times, error=ConnectionError):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise error("boom")
        return "ok"

    return flaky, calls


def test_retry_succeeds_after_failures(clock):
    flaky, calls = make_flaky(2)
    assert safe.retry(times=3, delay=1)(flaky)() == "ok"
    assert calls["n"] == 3
    assert clock.sleeps == [1, 1]


def test_retry_without_brackets():
    flaky, calls = make_flaky(2)
    assert safe.retry(flaky)() == "ok"


def test_retry_gives_up_and_raises():
    flaky, calls = make_flaky(5)
    with pytest.raises(ConnectionError):
        safe.retry(times=3)(flaky)()
    assert calls["n"] == 3


def test_retry_only_listed_exceptions():
    flaky, calls = make_flaky(1, error=KeyError)
    with pytest.raises(KeyError):
        safe.retry(times=3, exceptions=ConnectionError)(flaky)()
    assert calls["n"] == 1


def test_retry_keeps_function_name():
    @safe.retry(times=2)
    def my_function():
        return 1

    assert my_function.__name__ == "my_function"


def test_retry_bad_times():
    with pytest.raises(ValueError):
        safe.retry(times=0)


def test_timeout_returns_value_and_errors():
    @safe.timeout(seconds=1)
    def quick(x):
        return x * 2

    @safe.timeout(seconds=1)
    def broken():
        raise KeyError("x")

    assert quick(21) == 42
    with pytest.raises(KeyError):
        broken()


def test_timeout_too_slow():
    @safe.timeout(seconds=0.05)
    def slow():
        time.sleep(1)

    with pytest.raises(TimeoutError, match="slow\\(\\) took longer"):
        slow()


def test_timeout_needs_seconds():
    with pytest.raises(TypeError):
        safe.timeout(lambda: None)


def test_run():
    assert safe.run(int, "42") == 42
    assert safe.run(int, "oops") is None
    assert safe.run(int, "oops", default=0) == 0
    assert safe.run(int, "ff", base=16) == 255
