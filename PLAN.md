# Plan

Deadline 18:00 on 2026-11-07; the form opens at 16:00. Uploader: **TBD
(one person only)**. Team name: **TBD**.

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
5. **Freeze at 17:15.** Only fixes after that. Final `python -m submit`
   and upload by 17:40.
