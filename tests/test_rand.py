import string

import pytest

from easyutils import rand as r


def test_coin_and_dice():
    for _ in range(100):
        assert r.coin_flip() in ("heads", "tails")
        assert 1 <= r.dice() <= 6
        assert 1 <= r.dice(20) <= 20
    with pytest.raises(ValueError):
        r.dice(0)


def test_number():
    assert all(3 <= r.number(3, 5) <= 5 for _ in range(50))
    assert r.number(4, 4) == 4
    with pytest.raises(ValueError):
        r.number(5, 1)


def test_pick_and_pick_many():
    items = ["a", "b", "c"]
    assert r.pick(items) in items
    many = r.pick_many(items, 2)
    assert len(set(many)) == 2 and set(many) <= set(items)
    with pytest.raises(ValueError):
        r.pick([])
    with pytest.raises(ValueError):
        r.pick_many(items, 4)


def test_shuffle_keeps_original():
    items = list(range(20))
    shuffled = r.shuffle(items)
    assert items == list(range(20))
    assert sorted(shuffled) == items


def test_chance_edges():
    assert not any(r.chance(0) for _ in range(100))
    assert all(r.chance(100) for _ in range(100))
    with pytest.raises(ValueError):
        r.chance(150)


def test_password():
    for _ in range(50):
        pw = r.password(length=8)
        assert len(pw) == 8
        assert any(c in string.ascii_lowercase for c in pw)
        assert any(c in string.ascii_uppercase for c in pw)
        assert any(c in string.digits for c in pw)
        assert any(c in "!@#$%^&*-_=+?" for c in pw)
    plain = r.password(length=10, symbols=False)
    assert plain.isalnum()
    with pytest.raises(ValueError):
        r.password(length=3)
