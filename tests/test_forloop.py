import datetime as dt
import io

import pytest

from easyutils import forloop as fl


def test_every_runs_on_schedule(clock):
    start = clock.mono
    runs = [(n, clock.mono - start) for n in fl.every(seconds=10, times=3)]
    assert runs == [(0, 0), (1, 10), (2, 20)]


def test_every_does_not_drift_when_body_takes_time(clock):
    start = clock.mono
    moments = []
    for _ in fl.every(seconds=10, times=3):
        moments.append(clock.mono - start)
        clock.advance(3)  # body takes 3 seconds
    assert moments == [0, 10, 20]


def test_every_skips_missed_runs_when_body_is_too_slow(clock):
    start = clock.mono
    moments = []
    for _ in fl.every(seconds=10, times=3):
        moments.append(clock.mono - start)
        clock.advance(25)
    assert moments == [0, 30, 60]


def test_every_start_now_false_waits_first(clock):
    start = clock.mono
    first = next(fl.every(minutes=1, start_now=False))
    assert first == 0
    assert clock.mono - start == 60


def test_every_hour_is_one_hour(clock):
    start = clock.mono
    list(fl.every_hour(times=2))
    assert clock.mono - start == 3600


def test_every_second_and_minute(clock):
    start = clock.mono
    list(fl.every_second(times=3))
    assert clock.mono - start == 2
    start = clock.mono
    list(fl.every_minute(times=2))
    assert clock.mono - start == 60


@pytest.mark.parametrize("kwargs", [{}, {"seconds": -5}])
def test_every_rejects_bad_interval(kwargs):
    with pytest.raises(ValueError):
        next(fl.every(**kwargs))


def test_every_rejects_bad_times():
    with pytest.raises(ValueError):
        next(fl.every(seconds=1, times=-1))


def test_every_day_waits_for_the_clock_time(clock):
    # fake clock starts at 2026-01-01 08:00
    moments = []
    for _ in fl.every_day(at="09:30", times=3):
        moments.append(clock.wall)
        clock.advance(5)
    assert moments == [
        dt.datetime(2026, 1, 1, 9, 30),
        dt.datetime(2026, 1, 2, 9, 30),
        dt.datetime(2026, 1, 3, 9, 30),
    ]


def test_every_day_time_already_passed_today_means_tomorrow(clock):
    next(fl.every_day(at="07:00"))
    assert clock.wall == dt.datetime(2026, 1, 2, 7, 0)


@pytest.mark.parametrize("bad", ["9am", "25:00", "12", 930, "aa:bb"])
def test_every_day_bad_time_gives_helpful_error(bad):
    with pytest.raises(ValueError, match="09:00"):
        next(fl.every_day(at=bad))


def test_for_duration(clock):
    runs = 0
    for _ in fl.for_duration(seconds=10):
        runs += 1
        clock.advance(3)
    assert runs == 4  # starts at 0, 3, 6, 9


def test_times():
    assert list(fl.times(3)) == [0, 1, 2]
    assert list(fl.times(0)) == []
    with pytest.raises(ValueError):
        fl.times(-1)
    with pytest.raises(ValueError):
        fl.times(2.5)


def test_forever_until_break():
    seen = []
    for i in fl.forever():
        seen.append(i)
        if i == 4:
            break
    assert seen == [0, 1, 2, 3, 4]


def test_countdown():
    assert list(fl.countdown(5)) == [5, 4, 3, 2, 1]
    assert list(fl.countdown(3, 0)) == [3, 2, 1, 0]
    assert list(fl.countdown(0)) == []


def test_with_progress_yields_items_and_draws_bar():
    out = io.StringIO()
    items = list(fl.with_progress(["a", "b", "c", "d"], label="Work", width=4, stream=out))
    assert items == ["a", "b", "c", "d"]
    text = out.getvalue()
    assert "Work [----] 0/4" in text
    assert "Work [##--] 2/4" in text
    assert text.endswith("Work [####] 4/4\n")


def test_with_progress_accepts_generators_and_empty():
    out = io.StringIO()
    assert list(fl.with_progress((x for x in range(3)), stream=out)) == [0, 1, 2]
    out = io.StringIO()
    assert list(fl.with_progress([], stream=out)) == []
    assert "0/0" in out.getvalue()


def test_pairs():
    assert list(fl.pairs([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
    assert list(fl.pairs([1])) == []
    assert list(fl.pairs([])) == []


def test_chunks():
    assert list(fl.chunks([1, 2, 3, 4, 5], size=2)) == [[1, 2], [3, 4], [5]]
    assert list(fl.chunks(range(6), 3)) == [[0, 1, 2], [3, 4, 5]]
    assert list(fl.chunks([], 3)) == []
    with pytest.raises(ValueError):
        next(fl.chunks([1], 0))


def test_mark_last():
    assert list(fl.mark_last("abc")) == [("a", False), ("b", False), ("c", True)]
    assert list(fl.mark_last(["only"])) == [("only", True)]
    assert list(fl.mark_last([])) == []


# fake clock starts on Thursday 2026-01-01 at 08:00

def test_every_weekday_skips_the_weekend(clock):
    days = [clock.wall.strftime("%a %d") for _ in fl.every_weekday(at="09:00", times=4)]
    assert days == ["Thu 01", "Fri 02", "Mon 05", "Tue 06"]
    assert clock.wall.time() == dt.time(9, 0)


def test_every_weekend(clock):
    days = [clock.wall.strftime("%a %d") for _ in fl.every_weekend(at="10:00", times=3)]
    assert days == ["Sat 03", "Sun 04", "Sat 10"]


def test_every_week(clock):
    moments = [clock.wall for _ in fl.every_week(on="Mon", at="07:30", times=2)]
    assert moments == [dt.datetime(2026, 1, 5, 7, 30), dt.datetime(2026, 1, 12, 7, 30)]


def test_every_week_today_but_time_passed_means_next_week(clock):
    next(fl.every_week(on="thursday", at="07:00"))
    assert clock.wall == dt.datetime(2026, 1, 8, 7, 0)


def test_on_days_accepts_names_and_numbers(clock):
    days = [clock.wall.strftime("%a") for _ in fl.on_days(["mon", "Wednesday", 4], at="18:00", times=4)]
    assert days == ["Fri", "Mon", "Wed", "Fri"]


def test_on_days_single_day_string(clock):
    next(fl.on_days("sat", at="12:00"))
    assert clock.wall == dt.datetime(2026, 1, 3, 12, 0)


@pytest.mark.parametrize("bad", ["funday", "m", 7, -1, True])
def test_bad_day_gives_helpful_error(bad):
    with pytest.raises(ValueError, match="monday"):
        next(fl.on_days([bad]))


def test_on_days_needs_a_day():
    with pytest.raises(ValueError):
        next(fl.on_days([]))
