# Verification ledger

Append-only. Each row says what was proven, where, and by which run. "Built"
is never rounded up to "tested"; anything not listed here is unverified.

| Date | Level | Claim | Platforms | Evidence |
|---|---|---|---|---|
| 2026-11-07 | L1 | `equity.score7` ranks hands like `card_utils.evaluate` (9,000 random 5/6/7-card pairs, 3,000 shared-board pairs, 8 edge hands); preflop table and equity sanity | local, windows-x64 | `python -m pytest tests/test_strategy.py -q` 14:31, 17 passed (inside the 210 below). Red seen: no ace-low straights planted → 7 failed, e.g. `edge_hands_match_the_official_evaluator[wheel straight]` |
| 2026-11-07 | L1 | Engine and scoring suite unchanged by the strategy | local, windows-x64 | `commands.unit` 14:31, 210 passed |
| 2026-11-07 | L3 | Strategy v1 is a valid submission: pickles, plays from the pickle in a worker against every dummy with no faults or timeouts | local, windows-x64 | `python -m pytest tests/test_model.py -q` 14:31, 9 passed; `python -m submit --team dryrun` 14:31, "played legally against every dummy", no review flags, files: pkl, equity.py, model.py, opponent.py, preflop_table.py |
| 2026-11-07 | L3 | Strategy v1 strength, 1000 deals (2000 hands) per dummy, bb/100 ± 95% CI: fold +56.6 ± 2.2, call +399.3 ± 33.5, random +183.3 ± 37.2, tight +36.2 ± 10.9, equity +119.6 ± 25.0 (all ahead); shove +45.8 ± 48.2 (unclear) | local, windows-x64 | `python -m evals --deals 1000` 14:26 with SHOVE_RANGE 0.35, then `--opponents shove tight equity` 14:30 with SHOVE_RANGE 0.50 (the committed value; tight and equity identical) |

## Unverified

- Ahead of `shove`: the interval still includes 0.
- Any result against real teams' bots; beating the dummies predicts nothing.
- macOS and Linux: nothing has run there (the organisers' machine is unknown).
- The full L3 arena suite (`commands.integration`) was not rerun after v1;
  v1 changes no arena code.
