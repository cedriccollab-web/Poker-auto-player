# Strategy v1 — harder sparring measurements

Date: 2026-11-07. Timezone: Europe/London (GMT).
Started: **2026-11-07 14:52:52 GMT**. Finished: **2026-11-07 14:58:03 GMT**.
Platform: macOS arm64, Python 3.14.0 in `.venv`; Windows not run here.

## Revision and scope

Merged `origin/main` into `opponents`, fast-forwarding to
`9fb3d7a77cbfd674614a8dd2d1a6ead1fc01ae27`. This measures strategy v1 with
real opponent counts. Added only development sparring bots and pickle
legality tests; `model.py`, `equity.py`, `preflop_table.py` and `opponent.py`
are identical to that main revision. The measurement commit contains the
sparring code and pickles used here.

## Opponents

- pushfold: any pair, any ace, K9+, QT+, JT, suited or offsuit. This is
  382/1326 combinations (28.81%). Shoves when eligible, folds the rest;
  no limps. Calls only when an eligible hand cannot legally raise.
- nit: QQ+ and AK only, raises to `pot` clamped to the legal range on every
  street, otherwise checks/folds. Retains its starting-hand rule postflop.
- potbettor: pocket pairs preflop; a pair or better using hole cards
  postflop. Bets pot when checked to, calls when facing a bet, otherwise
  checks/folds. A shared board pair alone does not qualify.
- minraiser: minimum legal raise whenever possible, otherwise checks/calls.
- sharp: subclass of the unmodified `arena.dummies.EquityBot`, samples=400.
  Uses the stock evaluator and policy via a local EquityBot; persists only
  the plain RNG state (initial seed 79), continuing across hands.
- example: the pre-existing CLAUDE.md example bot, unchanged.

## Results

1000 duplicate deals = 2000 hands per opponent. Evaluation defaults: seed 0,
one run, default stacks and blinds. Units are big blinds won per 100 hands.
The ± values are 95% confidence-interval half-widths. Endpoints below are
computed from the tool's rounded displayed values. Faults are v1's faults
(the evaluator reports the first player's faults).

| Opponent | bb/100 | 95% half-width | 95% interval | Verdict / flag | Hands | V1 faults |
|---|---:|---:|---|---|---:|---:|
| pushfold | +1.8 | ±23.6 | [-21.8, +25.4] | **FLAG: unclear** | 2000 | 0 |
| nit | +50.2 | ±9.6 | [+40.6, +59.8] | ahead | 2000 | 0 |
| potbettor | +32.8 | ±15.9 | [+16.9, +48.7] | ahead | 2000 | 0 |
| minraiser | +351.1 | ±35.9 | [+315.2, +387.0] | ahead | 2000 | 0 |
| sharp | +128.1 | ±25.3 | [+102.8, +153.4] | ahead | 2000 | 0 |
| example | +40.6 | ±10.1 | [+30.5, +50.7] | ahead | 2000 | 0 |

**Flag: pushfold is unclear**, with interval [-21.8, +25.4] bb/100. No
opponent is behind. The other five are ahead with intervals above zero.
Zero v1 faults across all six matchups. These are supplied/development
opponents, not tournament outcome predictions. No strategy changes were
made in response to these measurements.

## Red evidence (L3 pickle legality)

Added one parametrized test case per new bot, first run before their
pickles existed. Every case failed with FileNotFoundError reported as a
worker seed fault, proving the tests reject missing/broken artifacts.
After implementation and packaging all five pass. Tests exercise both
500-chip and 60-chip stacks against random, checking faults for both seats.

Command: `python -m pytest tests/test_opponent.py::test_hard_sparring_pickles_play_legally -q`

```text
=========================== short test summary info ============================
FAILED tests/test_opponent.py::test_hard_sparring_pickles_play_legally[pushfold]
FAILED tests/test_opponent.py::test_hard_sparring_pickles_play_legally[nit]
FAILED tests/test_opponent.py::test_hard_sparring_pickles_play_legally[potbettor]
FAILED tests/test_opponent.py::test_hard_sparring_pickles_play_legally[minraiser]
FAILED tests/test_opponent.py::test_hard_sparring_pickles_play_legally[sharp]
5 failed in 0.80s
```

Policy spot checks also passed: exhaustive pushfold combination count,
nit range inclusion/exclusion and pot amount, potbettor board-pair rejection
and made-hand calls, minimum raise sizing, sharp sample count.

## Full requested test output (L1/L3 focused)

```text
$ python -m pytest tests/test_model.py tests/test_opponent.py -q
..............................                                           [100%]
30 passed in 9.96s
```

## Full requested measurement output

```text
$ python -m evals --deals 1000 --opponents bots/pushfold.pkl bots/nit.pkl bots/potbettor.pkl bots/minraiser.pkl bots/sharp.pkl bots/example.pkl
opponents                       your bb/100  verdict   hands faults  slowest
pushfold                      +1.8 ± 23.6    unclear    2000      0    0.00s
nit                          +50.2 ± 9.6       ahead    2000      0    0.00s
potbettor                    +32.8 ± 15.9      ahead    2000      0    0.00s
minraiser                   +351.1 ± 35.9      ahead    2000      0    0.00s
sharp                       +128.1 ± 25.3      ahead    2000      0    0.00s
example                      +40.6 ± 10.1      ahead    2000      0    0.00s
```
