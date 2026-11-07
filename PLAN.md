# Plan

Deadline 18:00 on 2026-11-07; the form opens at 16:00. Uploader: **TBD
(one person only)**. Team name: **prefer-not-to-say** (names must be
lower case: a-z, 0-9, `-`, `_`). Build: `python -m submit --team
prefer-not-to-say`; the files to upload are copied to `upload/`.

## Slices

1. **Strategy v1** (strategy). Status: tested locally on windows-x64
   (L1, L3); ahead of 5 of 6 dummies, `shove` unclear (+45.8 ± 48.2). Preflop ranges for 25 bb heads-up, postflop
   Monte Carlo equity against the price of calling, bet sizing.
   Done when: `tests/test_model.py` passes and `python -m evals` is `ahead`
   of every dummy bot at 1000 deals. Uploaded as soon as the form opens.
   - Ruling: own 7-card evaluator in `equity.py` instead of
     `card_utils.evaluate` — about 30x faster (126k vs 4k run-outs/s), so
     300 run-outs per decision cost ~3 ms and an evals run takes minutes —
     a ranking bug would misplay hands; guarded by `tests/test_strategy.py`
     against the official evaluator (9,000 random hands, 8 edge hands).
   - Ruling: the opponent's range is "the strongest X% of starting hands",
     narrowed by each raise — a cheap stand-in for hand reading — misjudges
     draws and made hands after the flop.
   - Ruling: a preflop shove is read as at least the top 35% — avoids
     folding everything to shove-happy bots — calls too wide against a
     tight shover until opponent stats say otherwise.
2. **Opponent stats** (opponents). Real counting in `opponent.py` per
   `docs/handoff/opponent-stats.md`, with L1 tests in
   `tests/test_opponent.py`. Done when: those tests pass, each shown red
   once, and `tests/test_model.py` still passes. Pushed to branch
   `opponents` by 16:45.
3. **Sparring bots** (opponents). `sparring.py` with bots that play like
   likely teams: the example bot from `CLAUDE.md`, a calling station, a
   maniac that raises most hands. Pickled into `bots/<name>.pkl` for
   `python -m evals --opponents bots/<name>.pkl`. Done when: each plays
   without faults and evals runs against it.
4. **Exploit** (strategy). After slice 2 merges, adjust play by the stats.
   Done when: evals against the sparring bots is better than v1 at 1000
   deals with intervals that do not overlap, or the change is dropped.
   Status: v2 tested locally on windows-x64 (L1, L3): better than v1 with
   non-overlapping intervals against tight (+59 vs +36) and example (+67 vs
   +41), no opponent worse. v1 is frozen in `snapshots/v1/` as an opponent.
   - Ruling: exploits key off fold_to_raise only (station and folder
     degrees, both 0 at the prior) — unknown teams get exactly v1's play —
     a team that folds preflop but calls postflop is misread.
   - v3: a preflop shove is read as the team's own shove rate (floor 12%)
     after 20 hands. pushfold +35.1 (v2 −3.9), intervals apart; shove and
     maniac slightly lower within noise.
   - Ruling: accept v3's small, non-significant dips against shove-everything
     bots — real teams are likelier to shove tight than to shove everything —
     costs a few bb/100 against a true maniac.
   - v4: after a postflop bet, the opponent's hand is weighted toward ones
     with something on the board (pair using a hole card, flush draw); a
     hand with nothing counts with weight 0.30 at prior aggression (0.10
     passive, 0.90 maniac). Beats v3 head to head +24.8 ± 20.0; equity
     bot +202 vs +145. The preflop-range narrowing per postflop raise is
     removed so the two do not double count.
   - Ruling: straight draws do not count as "something" — cheap to skip,
     the flush draw covers most semi-bluffs — overfolds a little against a
     bot that bets open-enders.
5. **Freeze at 17:15.** Only fixes after that. Final `python -m submit`
   and upload by 17:40.
