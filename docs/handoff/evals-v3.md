# Strategy v3 — regression and bluffer measurements

Date: 2026-11-07. Timezone: Europe/London (GMT).
Platform: macOS arm64, Python 3.14.0 in `.venv`; Windows not run here.

- Regression: **2026-11-07 15:27:52 GMT** to **2026-11-07 15:34:16 GMT**.
- Bluffer: **2026-11-07 15:35:02 GMT** to **2026-11-07 15:35:05 GMT**.
- Strategy revision: `bcdd1f0871515fe09fd903e8957478f79f96f34a`, fetched and
  fast-forward merged from origin/main into opponents before testing.

## Integrity and scope

No pulls or repository-file edits took place during either evaluation.
The regression finished and its checksum was checked before adding the
bluffer code or test. The bluffer test first failed because the class did
not exist; then implementation, pickle creation and all tests completed
before the separate bluffer evaluation started. No files were edited
until that evaluation also finished.

`model.py`, `equity.py`, `preflop_table.py`, and the entire `opponent.py`
are unchanged from `bcdd1f0` (verified with git diff). `md5 model.py` output
was identical at the start and end of both evaluations:

```text
MD5 (model.py) = 199de2c4ecc497ad6d673e7800f7afff
```

## Results and comparison with v2

Each matchup used 1000 duplicate deals (2000 hands), default seed 0 and
one run. Units: bb/100. The ± value is the 95% confidence-interval half-width;
interval endpoints use the tool's rounded displayed values. Faults are
v3's faults, as printed by evals.

| Opponent | V3 bb/100 ± 95% half-width | V3 95% interval | Verdict / flag | V2 bb/100 ± 95% half-width | Difference / comparison | V3 faults |
|---|---:|---|---|---:|---|---:|
| nit | +65.9 ± 10.5 | [+55.4, +76.4] | ahead | +65.9 ± 10.5 | +0.0 (identical result and CI) | 0 |
| potbettor | +67.4 ± 14.7 | [+52.7, +82.1] | ahead | +67.4 ± 14.7 | +0.0 (identical result and CI) | 0 |
| minraiser | +378.1 ± 38.8 | [+339.3, +416.9] | ahead | +378.1 ± 38.8 | +0.0 (identical result and CI) | 0 |
| sharp | +171.9 ± 27.0 | [+144.9, +198.9] | ahead | +171.9 ± 27.0 | +0.0 (identical result and CI) | 0 |
| equity | +145.4 ± 25.7 | [+119.7, +171.1] | ahead | +145.4 ± 25.7 | +0.0 (identical result and CI) | 0 |
| call | +468.8 ± 36.7 | [+432.1, +505.5] | ahead | +468.8 ± 36.7 | +0.0 (identical result and CI) | 0 |
| station | +468.8 ± 36.7 | [+432.1, +505.5] | ahead | +468.8 ± 36.7 | +0.0 (identical result and CI) | 0 |
| v2 | +0.0 ± 0.0 | [+0.0, +0.0] | **FLAG: unclear** | Not recorded | No v2 baseline in ledger | 0 |
| bluffer | +118.3 ± 47.8 | [+70.5, +166.1] | ahead | Not recorded | No v2 baseline in ledger | 0 |

**Flag: the v2 snapshot matchup is unclear**, exactly 0.0 ± 0.0. All eight
other opponents are ahead. None is behind, and v3 has zero faults.

The seven external regression opponents reproduce v2's displayed mean and
confidence interval exactly. The v2 reference numbers come from the
VERIFICATION.md rows "v2 vs the same decks as the v1 row above" (equity,
call, station) and "v2 vs the opponents role's harder bots" (nit,
potbettor, minraiser, sharp). Those reference runs were on Windows; this
run is on macOS. These results show no measured regression in the tested
matchups, not a claim of tournament strength or statistical equivalence on
all possible deals.

For `snapshots/v2/v2.pkl`, the ledger has no v2-versus-v2 baseline. Its
existing v3 row records 0.0 ± 0.0 against that snapshot; this run reproduces
that check. Do not substitute the ledger's v2-versus-v1 +2.1 ± 15.7 number:
that is a different opponent. Bluffer is new and has no v2 measurement in
VERIFICATION.md, so no v3-minus-v2 comparison is available for it.

## Bluffer definition and red/green evidence

`sparring.Bluffer`, pickled with protocol 4 to `bots/bluffer.pkl`:

- Preflop: checks when free; otherwise calls when the opponent's total
  street bet is at most 3 big blinds, folds to bigger totals, never raises.
- Postflop: when call_amount is zero, bets the pot with any cards (legal
  raise clamping; checks if raising is unavailable). When facing a bet or
  raise, folds. It does not inspect hole-card strength.

The new test checks the 3-BB boundary, folds above the boundary, pot bluffs
with weak cards on flop/turn/river, folds facing postflop aggression, and
checks when raising is unavailable. It then plays from the pickle against
random in real workers at both 500-chip and 60-chip stacks, asserting no
faults for either seat.

Red command: `python -m pytest tests/test_opponent.py::test_bluffer_pickle_plays_legally -q`

```text
F                                                                        [100%]
=================================== FAILURES ===================================
______________________ test_bluffer_pickle_plays_legally _______________________

    def test_bluffer_pickle_plays_legally():
>       from sparring import Bluffer
E       ImportError: cannot import name 'Bluffer' from 'sparring' (/Users/jeremyfung/Downloads/Poker/sparring.py)

tests/test_opponent.py:141: ImportError
=========================== short test summary info ============================
FAILED tests/test_opponent.py::test_bluffer_pickle_plays_legally - ImportErro...
1 failed in 0.06s
```

## Full requested regression test output

```text
$ python -m pytest tests/test_model.py tests/test_opponent.py -q
..............................                                           [100%]
30 passed in 9.56s
```

After adding bluffer, the same command was rerun before its evaluation:

```text
$ python -m pytest tests/test_model.py tests/test_opponent.py -q
...............................                                          [100%]
31 passed in 10.28s
```

## Full requested regression evaluation output

```text
$ python -m evals --deals 1000 --opponents bots/nit.pkl bots/potbettor.pkl bots/minraiser.pkl bots/sharp.pkl equity call bots/station.pkl snapshots/v2/v2.pkl
opponents                       your bb/100  verdict   hands faults  slowest
nit                          +65.9 ± 10.5      ahead    2000      0    0.00s
potbettor                    +67.4 ± 14.7      ahead    2000      0    0.00s
minraiser                   +378.1 ± 38.8      ahead    2000      0    0.00s
sharp                       +171.9 ± 27.0      ahead    2000      0    0.00s
equity                      +145.4 ± 25.7      ahead    2000      0    0.00s
call                        +468.8 ± 36.7      ahead    2000      0    0.00s
station                     +468.8 ± 36.7      ahead    2000      0    0.00s
v2                            +0.0 ± 0.0     unclear    2000      0    0.01s
```

## Full bluffer evaluation output

```text
$ python -m evals --deals 1000 --opponents bots/bluffer.pkl
opponents                       your bb/100  verdict   hands faults  slowest
bluffer                     +118.3 ± 47.8      ahead    2000      0    0.00s
```
