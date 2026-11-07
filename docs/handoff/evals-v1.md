# Strategy v1 measurement request — baseline available on origin/main

Date: 2026-11-07. Timezone: Europe/London (GMT).
Evaluation started: **2026-11-07 14:25:25 GMT**. Finished: **2026-11-07 14:26:50 GMT**.
Platform: macOS arm64, Python 3.14.0 in `.venv`.

## Revision caveat

**Strategy v1 was not available on origin/main.** Fetch, switch and merge
completed successfully, reporting already up to date. Main was
`31a258ba1bb0181b4d19baa2bf5b811bfaff7bc0`; the measured opponents branch was
`90507440ed3d99c20cfb728850df6d34a4f22b1b`.
`model.py` still returns call on every turn; `equity.py` and
`preflop_table.py` do not exist at those revisions. A second fetch after
the evaluation confirmed main was unchanged. These are measurements of
that available baseline together with the real opponent tracker, **not a
claim about strategy v1**. Repeat these commands after v1 is pushed.
No strategy, equity, preflop, engine or evaluator files were edited.

`ExampleBot` already matched the CLAUDE.md example in `sparring.py`.
`bots/example.pkl` was regenerated using pickle protocol 4 and verified
byte-identical to the committed file; station and maniac remain alongside it.

## Results

1000 duplicate deals = 2000 hands per opponent, seats exchanged; defaults:
seed 0, one run. Units: big blinds won per 100 hands. The ± value is the
tool's 95% confidence-interval half-width. Interval endpoints below use
those displayed rounded values.

| Opponent | bb/100 | 95% half-width | 95% interval | Verdict / flag | Hands | Faults |
|---|---:|---:|---|---|---:|---:|
| tight | -94.7 | ±24.1 | [-118.8, -70.6] | **FLAG: behind** | 2000 | 0 |
| equity | -253.7 | ±27.9 | [-281.6, -225.8] | **FLAG: behind** | 2000 | 0 |
| shove | +0.0 | ±0.0 | [+0.0, +0.0] | **FLAG: unclear** | 2000 | 0 |
| random | -6.1 | ±40.8 | [-46.9, +34.7] | **FLAG: unclear** | 2000 | 0 |
| call | +0.0 | ±0.0 | [+0.0, +0.0] | **FLAG: unclear** | 2000 | 0 |
| example | -105.2 | ±24.1 | [-129.3, -81.1] | **FLAG: behind** | 2000 | 0 |
| maniac | +0.0 | ±0.0 | [+0.0, +0.0] | **FLAG: unclear** | 2000 | 0 |
| station | +0.0 | ±0.0 | [+0.0, +0.0] | **FLAG: unclear** | 2000 | 0 |

**Every opponent is flagged:** behind against tight, equity and example;
unclear against shove, random, call, maniac and station. No opponent has
an ahead verdict. Zero faults in all eight matchups. This is a baseline
measurement, not a tournament prediction. Strategy owners should rerun
once their v1 is actually on main; no policy changes were made here.

## Full test output (L1/L3 focused)

With `.venv` activated:

```text
$ python -m pytest tests/test_model.py tests/test_opponent.py -q
.........................                                                [100%]
25 passed in 3.26s
```

## Full evaluation output

```text
$ python -m evals --deals 1000 --opponents tight equity shove random call bots/example.pkl bots/maniac.pkl bots/station.pkl
opponents                       your bb/100  verdict   hands faults  slowest
tight                        -94.7 ± 24.1     behind    2000      0    0.00s
equity                      -253.7 ± 27.9     behind    2000      0    0.00s
shove                         +0.0 ± 0.0     unclear    2000      0    0.00s
random                        -6.1 ± 40.8    unclear    2000      0    0.00s
call                          +0.0 ± 0.0     unclear    2000      0    0.00s
example                     -105.2 ± 24.1     behind    2000      0    0.00s
maniac                        +0.0 ± 0.0     unclear    2000      0    0.00s
station                       +0.0 ± 0.0     unclear    2000      0    0.00s
```
