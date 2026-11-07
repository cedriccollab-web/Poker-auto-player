# Team brief: poker bot

## The goal

We write one Python bot that plays heads-up no-limit Texas hold'em. Every
team's bot plays every other team's bot: 200 deals each way with the seats
swapped, every hand starting fresh at 500 chips with 10/20 blinds (25 big
blinds deep). The best average win rate (bb/100) takes the £300.
Submissions open at 16:00 and close at 18:00; the newest working upload is
the one that plays. The bot is the `Model` class in `model.py`.

## Who does what

| | Strategy: itsdanielyc + Claude Code | Opponents: you + Codex |
|---|---|---|
| Files | `model.py`, `equity.py` | `opponent.py`, `tests/test_opponent.py`, `sparring.py`, `bots/` |
| Branch | `main` | `opponents` (never `main`) |
| Job | What the bot does: which hands to play, win chance against the price of calling, bet sizes. Uploads v1 at 16:00, later uses your stats to exploit opponents, merges your branch | 1) Count each opponent's habits in `opponent.py`: fold-to-raise, aggression, VPIP, shove rate, with tests. 2) Practice bots in `sparring.py` that play like other teams |

Only touch your own files. The meeting point is
`docs/handoff/opponent-stats.md`: the method names and numbers in it are
fixed. If you need it changed, message first.

## How to drive Codex

1. `git pull`, then start Codex in the repo folder. First message:
   `Read docs/handoff/brief-opponents.md and follow it.`
2. Check it switched to the `opponents` branch: `git branch` shows
   `* opponents`. If it shows `main`, stop it.
3. Let it finish slice 2 (`opponent.py` and its tests) before slice 3
   (sparring bots). Slice 2 is the one the bot uses.
4. Before you believe "done", make it show you, with the output:
   - `python -m pytest tests/test_opponent.py -q` passes;
   - `python -m pytest tests/test_model.py -q` still says `9 passed`;
   - one test failing when it breaks the counting on purpose, then passing
     again once restored (proof the test can catch a bug).
5. Push: `git push -u origin opponents`, then message your partner.

Useful prompts:

- "Run the tests and paste the output."
- "Did you change any file outside opponent.py, sparring.py,
  tests/test_opponent.py and bots/?" The answer must be no.
- "Pickle the example bot from CLAUDE.md to bots/example.pkl and run
  python -m evals --opponents bots/example.pkl --deals 300."
- If Codex wants to edit `model.py`: say no. It writes what it needs into
  `docs/handoff/opponent-stats.md` instead, and you tell your partner.

## Never

- Push to `main`, or upload to the submission form (one uploader only).
- Edit the files headed `DO NOT CHANGE THIS CODE`, `engine.py`, `arena/` or
  `evals/`.
- Use `os`, `open`, `eval`, `subprocess` or the network: the organisers'
  review flags it.

## Timeline

- 16:00: strategy uploads v1.
- 16:45: `opponents` branch pushed: real stats, tests passing.
- 17:15: code freeze, fixes only.
- 17:40: final upload.

On a Mac, run `source .venv/bin/activate` first so `python` is the venv's.
