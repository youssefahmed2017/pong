# EasyUtils

Simple, readable helpers for everyday Python. Loops that read like English,
easy waiting, user input that re-asks on bad answers, pretty printing,
one-line file handling and more.

- **No dependencies**, just the Python standard library (Python 3.8+)
- **Names that read like English**
- **Friendly error messages** that tell you how to fix the problem

```python
from easyutils import forloop as fl

for _ in fl.every_hour():
    print("Another hour went by!")
```

## Install

```bash
pip install .            # from this folder
pip install -e ".[dev]"  # for development (adds pytest)
```

The package is imported as `easyutils`. Its install name is `easyutils-py`
because `easyutils` is already taken on PyPI.

## Modules

| Module | Suggested name | What it's for |
|---|---|---|
| `forloop` | `fl` | Loops that read like English |
| `loopvars` | `lv` | Values you track inside loops |
| `wait` | `w` | Pausing and timing |
| `ask` | `ask` | Asking the user for input |
| `say` | `say` | Pretty printing |
| `files` | `ef` | One-line file reading and writing |
| `safe` | `safe` | Error handling without try/except |
| `rand` | `r` | Randomness made simple |

### `forloop`: loops that read like English

```python
from easyutils import forloop as fl

for _ in fl.every_hour(): ...              # now, then every hour, forever
for run in fl.every(seconds=10, times=5): ...  # 5 runs, 10 seconds apart
for _ in fl.every_day(at="09:00"): ...     # every day at 9 in the morning
for _ in fl.every_second(): ...
for _ in fl.every_minute(): ...

for i in fl.times(5): ...                  # 0, 1, 2, 3, 4
for i in fl.forever(): ...                 # until you `break`
for _ in fl.for_duration(minutes=2): ...   # keep going for 2 minutes
for n in fl.countdown(10): ...             # 10, 9, ..., 1

for photo in fl.with_progress(photos, label="Resizing"): ...  # progress bar
for a, b in fl.pairs([1, 2, 3, 4]): ...    # (1, 2), (2, 3), (3, 4)
for group in fl.chunks(data, size=3): ...  # [1, 2, 3], [4, 5, 6], ...
for name, is_last in fl.mark_last(names): ...
```

Timed loops (`every...`) yield the run number (0, 1, 2, ...) and keep a steady
rhythm even if your loop body takes a while. If the body takes longer than
the interval, missed runs are skipped.

### `loopvars`: values you track inside loops

```python
from easyutils import loopvars as lv

count = lv.Counter()
count.up(); count.up(by=5); count.down(); count.reset()

total = lv.Total()
for price in [3, 9, 6]:
    total.add(price)
total.sum, total.count, total.average, total.min, total.max   # 18, 3, 6.0, 3, 9

seen = lv.Seen()
for email in emails:
    if seen.first_time(email):
        send_welcome(email)

timer = lv.LoopTimer()
for job in jobs:
    run(job)
    print(f"took {timer.tick():.2f}s")
print(f"average {timer.average:.2f}s")
```

### `wait`: pausing and timing

```python
from easyutils import wait as w

w.seconds(5); w.minutes(2); w.hours(1)
w.until("17:30")                                  # next time the clock shows 17:30
w.until(datetime(2030, 1, 1))                     # a specific moment
w.until(lambda: ef.exists("done.txt"), check_every=5, timeout=60)  # True or False

with w.stopwatch() as sw:
    do_work()
print(f"took {sw.elapsed:.1f} seconds")
```

### `ask`: user input

```python
from easyutils import ask

name = ask.text("What's your name? ")
age = ask.number("How old are you? ", whole=True, min=0, max=130)
again = ask.yes_no("Play again?", default=True)
color = ask.choice("Pick a color:", ["red", "green", "blue"])
```

Bad answers get a short explanation and the question is asked again.

### `say`: pretty printing

```python
from easyutils import say

say.success("Saved!")      # ✔ Saved!   (green)
say.error("Oops")          # ✘ Oops     (red)
say.warning("Careful")     # ! Careful  (yellow)
say.info("FYI")            # i FYI      (blue)
say.box("Welcome!")
say.table([{"name": "Ann", "score": 12}, {"name": "Bob", "score": 9}])
```

Colors are only used in a real terminal. Set `NO_COLOR=1` to turn them off,
or `FORCE_COLOR=1` to always use them.

### `files`: one-line file handling

```python
from easyutils import files as ef

ef.write("notes/today.txt", "Hello")   # creates the notes folder if needed
ef.append("notes/today.txt", "\nMore")
text = ef.read("notes/today.txt")

ef.write_json("save.json", {"level": 3})
data = ef.read_json("save.json")

for line in ef.lines("big.log"): ...   # one line at a time, newline removed
ef.exists("save.json"); ef.delete("save.json")
ef.list_files("photos", "*.jpg")
```

### `safe`: error handling

```python
from easyutils import safe

@safe.retry(times=3, delay=2)          # try up to 3 times, 2 seconds apart
def download(): ...

@safe.timeout(seconds=5)               # raise TimeoutError after 5 seconds
def slow_thing(): ...

safe.run(int, "oops", default=0)       # 0 instead of a crash
```

### `rand`: randomness

```python
from easyutils import rand as r

r.coin_flip()          # "heads" or "tails"
r.dice(); r.dice(20)   # 1-6, 1-20
r.number(1, 100)
r.pick(items); r.pick_many(items, 3); r.shuffle(items)
r.chance(30)           # True about 30% of the time
r.password(length=16)  # strong password made with the `secrets` module
```

## Try the demo

```bash
PYTHONPATH=src python examples/demo.py
```

## Running the tests

```bash
pip install pytest
python -m pytest
```

The timed loops are tested with a fake clock, so the whole suite runs in
under a second.

## License

MIT. See [LICENSE](LICENSE).
