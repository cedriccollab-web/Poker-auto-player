# Submission: Prefer not to say

Team **Prefer not to say** (pickle name `prefer-not-to-say`). The bot is
exactly these five files at the repository root, on branch `main`:

| File | What it is |
|---|---|
| `prefer-not-to-say.pkl` | `pickle.dump(Model())`, built by `python -m submit --team prefer-not-to-say` |
| `model.py` | the `Model` class: the strategy |
| `equity.py` | hand evaluator and Monte Carlo equity |
| `opponent.py` | per-team opponent statistics |
| `preflop_table.py` | starting-hand equities (data) |

To rebuild and check it from a clean clone:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m submit --team prefer-not-to-say
```

That lists the same five files, plays the model from a clean copy of just
those files against every dummy bot (no faults), and the code review flags
nothing in them. Only the standard library (`random`) and the arena's own
modules are imported; no files, network or engine internals.

**Not part of the bot** (development only, never imported by `model.py`):
`sparring.py` and `bots/` (practice opponents), `snapshots/` (frozen earlier
versions used as test opponents), `tests/`, `docs/`. The organisers' files
(`card_utils.py`, `player_action.py`, `game_state.py`, `game_interface.py`,
`engine.py`, `arena/`, `evals/`, `submit.py`) are unchanged from upstream.
