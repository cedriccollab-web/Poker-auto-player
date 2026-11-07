# Plan

Deadline 18:00 on 2026-11-07; the form opens at 16:00. Uploader: **TBD
(one person only)**. Team name: **TBD**.

## Slices

1. **Strategy v1** (strategy). Preflop ranges for 25 bb heads-up, postflop
   Monte Carlo equity against the price of calling, bet sizing.
   Done when: `tests/test_model.py` passes and `python -m evals` is `ahead`
   of every dummy bot at 1000 deals. Uploaded as soon as the form opens.
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
