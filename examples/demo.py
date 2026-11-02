"""A quick tour of EasyUtils. Run it with:  python examples/demo.py"""

from easyutils import forloop as fl
from easyutils import loopvars as lv
from easyutils import rand as r
from easyutils import say
from easyutils import wait as w

say.box("EasyUtils demo")

# Count down, one number per second
for n in fl.countdown(3):
    print(n)
    w.seconds(1)
say.success("Lift off!")

# Roll some dice and keep score
total = lv.Total()
for _ in fl.with_progress(range(20), label="Rolling dice"):
    total.add(r.dice())
    w.seconds(0.05)
say.info(f"Average roll: {total.average:.2f} (lowest {total.min}, highest {total.max})")

# Run something on a schedule
with w.stopwatch() as sw:
    for run in fl.every(seconds=0.5, times=3):
        print(f"run {run}: {r.coin_flip()}")
say.info(f"3 scheduled runs took {sw.elapsed:.1f}s")

# A little table
say.table(
    [
        {"name": "Ann", "score": r.number(1, 100)},
        {"name": "Bob", "score": r.number(1, 100)},
    ]
)

say.warning(f"Your new password: {r.password()}")
