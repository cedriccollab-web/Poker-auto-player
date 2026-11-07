# Verification ledger

Append-only. Each row says what was proven, where, and by which run. "Built"
is never rounded up to "tested"; anything not listed here is unverified.

| Date | Level | Claim | Platforms | Evidence |
|---|---|---|---|---|
| 2026-11-07 | L1 | `equity.score7` ranks hands like `card_utils.evaluate` (9,000 random 5/6/7-card pairs, 3,000 shared-board pairs, 8 edge hands); preflop table and equity sanity | local, windows-x64 | `python -m pytest tests/test_strategy.py -q` 14:31, 17 passed (inside the 210 below). Red seen: no ace-low straights planted → 7 failed, e.g. `edge_hands_match_the_official_evaluator[wheel straight]` |
| 2026-11-07 | L1 | Engine and scoring suite unchanged by the strategy | local, windows-x64 | `commands.unit` 14:31, 210 passed |
| 2026-11-07 | L3 | Strategy v1 is a valid submission: pickles, plays from the pickle in a worker against every dummy with no faults or timeouts | local, windows-x64 | `python -m pytest tests/test_model.py -q` 14:31, 9 passed; `python -m submit --team dryrun` 14:31, "played legally against every dummy", no review flags, files: pkl, equity.py, model.py, opponent.py, preflop_table.py |
| 2026-11-07 | L3 | Strategy v1 strength, 1000 deals (2000 hands) per dummy, bb/100 ± 95% CI: fold +56.6 ± 2.2, call +399.3 ± 33.5, random +183.3 ± 37.2, tight +36.2 ± 10.9, equity +119.6 ± 25.0 (all ahead); shove +45.8 ± 48.2 (unclear) | local, windows-x64 | `python -m evals --deals 1000` 14:26 with SHOVE_RANGE 0.35, then `--opponents shove tight equity` 14:30 with SHOVE_RANGE 0.50 (the committed value; tight and equity identical) |
| 2026-11-07 | L1, L3 | v1 merged with the opponents branch: unit suite incl. `tests/test_opponent.py`; bot check; submit dry run still lists pkl, equity.py, model.py, opponent.py, preflop_table.py with no flags | local, windows-x64 | `commands.unit` 14:39, 226 passed; `pytest tests/test_model.py tests/test_opponent.py -q` 14:39, 25 passed; `python -m submit --team dryrun` 14:39 |
| 2026-11-07 | L3 | v1 + real opponent stats, 1000 deals per opponent, bb/100 ± 95% CI, all ahead: tight +36.0 ± 8.6, equity +133.1 ± 24.4, shove +148.4 ± 54.0, random +154.8 ± 39.0, call +413.8 ± 34.0, example +40.6 ± 10.1, maniac +190.7 ± 50.7, station +413.8 ± 34.0 | local, windows-x64 | `python -m evals --deals 1000 --opponents tight equity shove random call bots/example.pkl bots/maniac.pkl bots/station.pkl` 14:39 to 14:44 on merge `9dcf991` |
| 2026-11-07 | L1, L3 | v2 (per-opponent exploits from fold_to_raise): `_profile` neutral at the prior, stations and folders read correctly; unit suite; bot check | local, windows-x64 | `pytest tests/test_strategy.py -q` 14:57, 23 passed; red: station threshold moved to 0.30 → 2 failed (`profile_reads_stations_and_folders[0.05-1.0-0.0]`, `[0.25-0.5-0.0]`); `commands.unit` 14:56, 226 passed; `pytest tests/test_model.py -q` 14:56, 9 passed |
| 2026-11-07 | L3 | v2 vs the same decks as the v1 row above, bb/100 ± 95% CI: v1 snapshot +2.1 ± 15.7 (unclear), tight +59.1 ± 10.1, equity +145.4 ± 25.7, shove +150.8 ± 53.6, random +191.2 ± 38.4, call +468.8 ± 36.7, example +66.7 ± 10.8, maniac +195.4 ± 51.1, station +468.8 ± 36.7. Better than v1 with non-overlapping intervals against tight and example; no opponent worse | local, windows-x64 | `python -m evals --deals 1000 --opponents snapshots/v1/v1.pkl tight equity shove random call bots/example.pkl bots/maniac.pkl bots/station.pkl` 14:58 to 15:03, model.py md5 `ef26e4b7…` at start and end. An earlier run was stopped because a test mutation touched model.py mid-run; its numbers are discarded |

## Unverified

- ~~Ahead of `shove`~~: proven with opponent stats in the row above.
- Any result against real teams' bots; beating the dummies predicts nothing.
- macOS and Linux: nothing has run there (the organisers' machine is unknown).
- The full L3 arena suite (`commands.integration`) was not rerun after v1;
  v1 changes no arena code.

## Opponents role entries (macOS arm64, from branch opponents)

## 2026-11-07 — opponents slices 2 and 3

Platform: macOS arm64, Python 3.14 (.venv); Windows not run.

- L1: `python -m pytest -q --ignore=tests/test_model.py --ignore=tests/arena_tests`: 209 passed.
- L3: `python -m pytest tests/test_model.py tests/arena_tests -q`: 219 passed, 6 skipped.
- Focused L1/L3: `python -m pytest tests/test_opponent.py tests/test_model.py -q`: 25 passed.
- Every new opponent test was observed red via deliberate count/prior/guard mutations; the three sparring tests were red with a broken seed. Mutations restored before final green runs.
- Packaging: `python -m submit --team opponents_check`: clean, all dummy games legal.
- Evals: 1000 duplicate deals (2000 hands) each against three sparring pickles and tight/equity; zero faults. These measure the unchanged calling baseline, not a strategy improvement.

Full commands, evidence and numbers: [opponents verification](docs/handoff/opponents-verification.txt).

## 2026-11-07 — measurement request, 2026-11-07 14:25:25 GMT to 2026-11-07 14:26:50 GMT

Platform: macOS arm64, .venv Python 3.14; Windows not run.

- Focused L1/L3: `python -m pytest tests/test_model.py tests/test_opponent.py -q`: 25 passed in 3.26s.
- `python -m evals --deals 1000 --opponents tight equity shove random call bots/example.pkl bots/maniac.pkl bots/station.pkl`: 2000 hands per opponent, zero faults. Three behind and five unclear.
- origin/main still at `31a258b`; strategy v1 absent. Measured `9050744` (calling template plus opponent tracker). No strategy edits.
- Complete outputs and intervals: [measurement report](docs/handoff/evals-v1.md).

## 2026-11-07 — harder sparring, 2026-11-07 14:52:52 GMT to 2026-11-07 14:58:03 GMT

Platform: macOS arm64, Python 3.14.0 (.venv). Base strategy: `9fb3d7a`.

- L3 red/green: five new pickle-legality cases failed before the pickles existed (5 failed in 0.80s), then passed with the real artifacts; normal/short stacks, both seats fault-free.
- Focused L1/L3: `python -m pytest tests/test_model.py tests/test_opponent.py -q`: 30 passed in 9.96s.
- `python -m evals --deals 1000 --opponents bots/pushfold.pkl bots/nit.pkl bots/potbettor.pkl bots/minraiser.pkl bots/sharp.pkl bots/example.pkl`: 2000 hands per opponent. V1 bb/100 ± 95% half-width: pushfold +1.8 ± 23.6 (unclear, flagged); nit +50.2 ± 9.6, potbettor +32.8 ± 15.9, minraiser +351.1 ± 35.9, sharp +128.1 ± 25.3, example +40.6 ± 10.1 (all five ahead). Zero v1 faults.
- No strategy files or opponent interface changed. Full outputs, intervals and bot definitions: [hard sparring report](docs/handoff/evals-v1-hard.md).
