import pytest

from easyutils import loopvars as lv


def test_counter():
    c = lv.Counter()
    assert c.up() == 1
    assert c.up(by=5) == 6
    assert c.down() == 5
    assert c == 5
    assert int(c) == 5
    assert c.reset() == 0
    assert lv.Counter(start=10).reset() == 10
    assert repr(lv.Counter(3)) == "Counter(3)"


def test_total():
    t = lv.Total()
    assert t.average is None and t.min is None and t.max is None
    for n in [3, 9, 6]:
        t.add(n)
    assert (t.sum, t.count, t.average, t.min, t.max) == (18, 3, 6.0, 3, 9)
    t.reset()
    assert (t.sum, t.count, t.average) == (0, 0, None)


def test_total_rejects_non_numbers():
    with pytest.raises(TypeError):
        lv.Total().add("5")
    with pytest.raises(TypeError):
        lv.Total().add(True)


def test_seen():
    seen = lv.Seen()
    assert seen.first_time("a") is True
    assert seen.first_time("a") is False
    assert seen.first_time("b") is True
    seen.add("c")
    assert "c" in seen
    assert "z" not in seen
    assert len(seen) == 3


def test_loop_timer(clock):
    timer = lv.LoopTimer()
    assert timer.average is None
    clock.advance(2)
    assert timer.tick() == 2
    clock.advance(4)
    assert timer.tick() == 4
    assert timer.last == 4
    assert timer.count == 2
    assert timer.average == 3
