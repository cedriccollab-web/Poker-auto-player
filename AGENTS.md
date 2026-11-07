# Pokerbot (Great Uni Hack, Manchester AI Society)

A Python bot for heads-up no-limit Texas hold'em. The bot is `Model` in
`model.py`; it is pickled and submitted with its `.py` files, then plays a
round robin against every other team's bot (duplicate deals, seats swapped,
best bb/100 wins). Challenge site: https://poker-arena-site.vercel.app/#/ .
Upstream: https://github.com/Manchester-AI-Society/poker_bot (remote
`upstream`). Submissions open 16:00 and close 18:00 on 2026-11-07; the
newest working upload before 18:00 is the one that plays.

The full game rules, the `GameStateView` API and the common mistakes are in
`CLAUDE.md` ("For bot authors"). Read it before touching `model.py`.

## Commands

Run from the repo root with the venv active (`.venv\Scripts\activate` on
Windows, `source .venv/bin/activate` elsewhere), so `python` is the venv's.

- setup: `python -m venv .venv` then `pip install -r requirements-dev.txt`
- unit (L1, engine and scoring, about 5 s): `python -m pytest -q --ignore=tests/test_model.py --ignore=tests/arena_tests`
- integration (L3, worker processes, about 3 min on Windows): `python -m pytest tests/test_model.py tests/arena_tests -q`
- is my bot a valid submission (about 10 s): `python -m pytest tests/test_model.py -q`
- how strong is it: `python -m evals` (add `--deals 1000`, `--opponents tight equity`, `--table`)
- submit dry run: `python -m submit --team <team>` (writes `<team>.pkl`, lists the files to upload, shows what the code review flags)

## Layout

- `model.py`: the bot. The one file we write; helper modules go flat next to it.
- `card_utils.py`, `player_action.py`, `game_state.py`, `game_interface.py`:
  the organisers' public contract, headed `DO NOT CHANGE THIS CODE`.
- `engine.py`: plays one hand. `arena/`: matches, worker processes, vetting,
  dummy bots (`arena/dummies.py`). `evals/`: bb/100 with confidence intervals.
- `submit.py`: builds and checks the submission.
- `tests/`: pytest + Hypothesis. `tests/test_model.py` checks our `Model`.

## Rules that are not negotiable

1. Edit only `model.py` and new flat files next to it. Never edit the
   contract files or the engine: the organisers' copies are what play.
2. The model is pickled: plain-data attributes only (numbers, lists, dicts,
   numpy arrays, weights). No lambdas, files, sockets, threads, generators.
   Weights and data load in `__init__`; nothing on disk exists at play time.
3. No `os`, `subprocess`, `socket`, `open`, `eval`/`exec`, network, or
   engine internals (`_state`, `__globals__`, `_getframe`): flagged code
   waits for a human review, and some of it is refused.
4. Every move must return within 10 s. A timeout kills the bot for the rest
   of that match.
5. Use only the `GameStateView` names listed in `CLAUDE.md`; any other name
   raises `AttributeError`.
6. `python -m pytest tests/test_model.py -q` and `python -m submit --team
   <team>` must both be clean before anything is uploaded.

## Ownership (two people, two agents)

- **strategy** (itsdanielyc, Claude Code): `model.py`, `equity.py`,
  `tests/test_strategy.py`. Works on `main`; pushes only when
  `tests/test_model.py` passes, so `main` is always submittable.
- **opponents** (cedriccollab-web, Codex): `opponent.py`, `sparring.py`,
  `tests/test_opponent.py`, `bots/`. Works on branch `opponents`; strategy
  merges it into `main` after the bot check passes.
- **shared**: `docs/handoff/`, `PLAN.md`, `AGENTS.md`, `keel.json`. The seam
  between roles is `docs/handoff/opponent-stats.md`. A need outside your
  files is a change to that document, not an edit to the other role's file.
- Never edit the other role's files. `git pull --rebase` before every push.
- One person uploads the submission (named in `PLAN.md`), never both: the
  newest working upload is the one that plays.

<!-- keel:start -->
## Keel

This repository uses Keel (`keel.json` at the root). Commands per testing
level are listed there; the testing doctrine is in the `keel-test` skill;
`VERIFICATION.md` is the append-only ledger of what has been proven and
where. Rules: name the level, platform and run behind every "tested"; a new
test proves it can fail first; flaky tests are quarantined, not deleted.

- Levels in use: L1 unit (`commands.unit`) and L3 integration
  (`commands.integration`, real worker processes). No lint, contract, UI or
  E2E levels exist; they are `null` in `keel.json`, not gaps to fill for a bot.
- "Tested" for a bot change means `tests/test_model.py` passed. "Stronger"
  means an `evals` run whose 95% interval excludes 0, with the deals and
  opponents named. Beating the dummy bots is not a tournament prediction.
- Correction to `CLAUDE.md`: its "about 30 s in total" for the suite holds
  on Linux; on Windows the full suite took 3 min 11 s (412 passed, 6
  skipped: one Linux-only, five need the organiser's gitignored site files).
<!-- keel:end -->
