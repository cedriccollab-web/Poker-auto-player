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
| 2026-11-07 | L3 | v2 vs the opponents role's harder bots, bb/100 ± 95% CI: pushfold −3.9 ± 23.8 (unclear), nit +65.9 ± 10.5, potbettor +67.4 ± 14.7, minraiser +378.1 ± 38.8, sharp +171.9 ± 27.0. Same decks as the opponents role's v1 row (`docs/handoff/evals-v1-hard.md`): v2 better against all but pushfold | local, windows-x64 | `python -m evals --deals 1000 --opponents bots/pushfold.pkl bots/nit.pkl bots/potbettor.pkl bots/minraiser.pkl bots/sharp.pkl` 15:05 to 15:17, model.py md5 `ef26e4b7…` |
| 2026-11-07 | L3 | Cross-platform determinism: v1 vs example is +40.6 ± 10.1 on both macOS arm64 (opponents role) and windows-x64 (this ledger) from the same seed | macOS arm64, windows-x64 | `docs/handoff/evals-v1-hard.md` and the v1 + stats row above |
| 2026-11-07 | L1 | v3 shove read: a preflop all-in is read as the team's own shove rate (floor 12%) after 20 hands, `SHOVE_RANGE` before | local, windows-x64 | `pytest tests/test_strategy.py -k shove` red on v2 (0.87 read for a 29% shover; 4 failed), then `commands.unit` 15:18, 241 passed; `pytest tests/test_model.py -q` 15:18, 9 passed |
| 2026-11-07 | L3 | v3 strength, same decks as v2, bb/100 ± 95% CI: pushfold +35.1 ± 15.0 (v2 −3.9 ± 23.8; intervals do not overlap), shove +136.0 ± 53.6 (v2 +150.8), random +189.8 ± 38.3 (v2 +191.2), maniac +166.9 ± 50.9 (v2 +195.4), example +66.7 ± 10.8 and tight +59.1 ± 10.1 (unchanged), v2 snapshot +0.0 ± 0.0 (they never face each other's shove). Ahead of all 7 | local, windows-x64 | `python -m evals --deals 1000 --opponents bots/pushfold.pkl shove random bots/maniac.pkl bots/example.pkl tight snapshots/v2/v2.pkl` 15:19 to 15:20, model.py md5 `199de2c4…` at start and end |
| 2026-11-07 | L1, L3 | v4 postflop hand reading: `has_something` (pair using a hole card, or a flush draw before the river) and `equity(..., bluff=)` weighting; unit suite; bot check | local, windows-x64 | red first: `pytest tests/test_strategy.py -k "something or postflop_bet"` → AttributeError, no `has_something`; then `commands.unit` 15:26, 248 passed; `pytest tests/test_model.py -q` 15:26, 9 passed |
| 2026-11-07 | L3 | v4 strength, same decks, bb/100 ± 95% CI: v3 snapshot +24.8 ± 20.0 (ahead head to head), equity +201.8 ± 29.8 (v2 +145.4 ± 25.7, intervals apart), potbettor +73.9 ± 13.8, nit +63.9 ± 11.0, example +69.1 ± 10.1, tight +59.5 ± 10.0, maniac +174.9 ± 51.3, pushfold +35.1 ± 15.0, random +166.7 ± 37.5, station +468.8 ± 36.7. Ahead of all 10; no change outside its interval for the worse | local, windows-x64 | `python -m evals --deals 1000 --opponents snapshots/v3/v3.pkl bots/example.pkl bots/potbettor.pkl bots/nit.pkl tight bots/maniac.pkl bots/pushfold.pkl random bots/station.pkl equity` 15:27 to 15:32, md5 model.py `fd4a525f…`, equity.py `e06b541b…` at start and end |
| 2026-11-07 | L3 | v4 does not overfold to bluffs: bluffer (bets the pot whenever checked to, any cards) +123.9 ± 47.0, v3 +118.3 ± 47.8 on the opponents role's run | local, windows-x64 | `python -m evals --deals 1000 --opponents bots/bluffer.pkl` 15:40, md5 model.py `fd4a525f…`, equity.py `e06b541b…` at start and end; v3 figure from `docs/handoff/evals-v3.md` |
| 2026-11-07 | L3 | v4 vs the rest: minraiser +377.2 ± 38.4, call +468.8 ± 36.7, shove +136.0 ± 53.6, sharp +192.1 ± 30.2 (v3 +171.9). v4 is ahead of all 15 opponents measured | local, windows-x64 | `python -m evals --deals 1000 --opponents bots/minraiser.pkl call shove bots/sharp.pkl` 15:41 to 15:55, md5 model.py `fd4a525f…`, equity.py `e06b541b…` at start and end |
| 2026-11-07 | L1, L3 | Single-file bot: `model.py` is generated from strategy.py, equity.py, opponent.py, preflop_table.py and imports only `random`, `card_utils`, `game_state`, `player_action`; submit lists only `prefer-not-to-say.pkl` and `model.py`; the review flags nothing; the pickle names only `model.Model`, `model.OpponentStats` | local, windows-x64 | `tests/test_bundle.py`: red on a stale bundle (strategy docstring changed) and on a copy with `from equity import score7` added (`{'equity'}`), then green; `commands.unit` 16:10, 253 passed; `pytest tests/test_model.py -q` 16:10, 9 passed; `python -m submit --team prefer-not-to-say` 16:10; `arena.vet.scan_source` / `scan_pickle` 16:10 |
| 2026-11-07 | L3 | The bundled `model.py` plays exactly like v4: the same evals run reproduces every bb/100, interval, verdict, hand count and fault count of the v4 row for all 10 opponents (only the wall-clock "slowest" column differs) | local, windows-x64 | `python -m evals --deals 1000 --opponents snapshots/v3/v3.pkl bots/example.pkl bots/potbettor.pkl bots/nit.pkl tight bots/maniac.pkl bots/pushfold.pkl random bots/station.pkl equity` 16:11 to 16:17, md5 model.py `595b0e15…` at start and end; compared column by column with the 15:27 run |

## Unverified

- ~~v4 vs sharp, minraiser, call, shove~~: proven in the row above.
- Any result against real teams' bots; beating these opponents predicts
  nothing about the tournament.
- ~~v3 vs nit, potbettor, minraiser, sharp, equity, call, station~~: run by
  the opponents role on macOS arm64 (`docs/handoff/evals-v3.md`),
  identical to v2.
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

## 2026-11-07 — v3 regression and bluffer (opponents role)

Platform: macOS arm64, Python 3.14.0 (.venv); strategy `bcdd1f0`.

- Focused L1/L3: `python -m pytest tests/test_model.py tests/test_opponent.py -q`: 30 passed in 9.56s before regression; 31 passed in 10.28s after bluffer. Bluffer test red first (missing class, 1 failed in 0.06s), then green, including worker pickle legality at normal and short stacks.
- Regression: `python -m evals --deals 1000 --opponents bots/nit.pkl bots/potbettor.pkl bots/minraiser.pkl bots/sharp.pkl equity call bots/station.pkl snapshots/v2/v2.pkl`, 2026-11-07 15:27:52 GMT to 2026-11-07 15:34:16 GMT. Means/95% half-widths: nit +65.9 ± 10.5, potbettor +67.4 ± 14.7, minraiser +378.1 ± 38.8, sharp +171.9 ± 27.0, equity +145.4 ± 25.7, call +468.8 ± 36.7, station +468.8 ± 36.7 (all ahead, all identical to v2); v2 snapshot 0.0 ± 0.0 (unclear, flagged).
- `python -m evals --deals 1000 --opponents bots/bluffer.pkl`, 2026-11-07 15:35:02 GMT to 2026-11-07 15:35:05 GMT: +118.3 ± 47.8 bb/100, ahead. No v2 bluffer baseline exists in the ledger.
- All matchups 2000 hands, zero v3 faults. `md5 model.py` at start/end of both runs: `199de2c4ecc497ad6d673e7800f7afff`. No files changed or pulls during evaluation. Strategy files and opponent interface unchanged.
- Full output, intervals and v2 comparisons: [v3 measurements](docs/handoff/evals-v3.md).
