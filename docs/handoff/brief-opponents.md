You are the **opponents** role on pokerbot, a heads-up no-limit hold'em
bot for a hackathon (Keel project). Read AGENTS.md first, then CLAUDE.md
"For bot authors", PLAN.md slices 2 and 3, docs/handoff/opponent-stats.md.

Branch: `git switch -c opponents` (cut from main) before the first commit.
Push it with `git push -u origin opponents`. Never push to main.
You own: opponent.py, sparring.py, tests/test_opponent.py, bots/.
You do not edit: model.py, equity.py, the DO NOT CHANGE files, engine.py,
arena/, evals/. A need there is a change to docs/handoff/opponent-stats.md.

Slice 2: replace the stub's priors in opponent.py with real counting.
The interface (names, arguments, [0, 1] ranges, priors for an unseen team,
the blend formula) is agreed: keep it exactly. Done when tests in
tests/test_opponent.py pass for every stat, the prior, the blend, unknown
teams and pickling, each shown red once by breaking the count; and
`python -m pytest tests/test_model.py -q` still passes. Target 16:45.

Slice 3: sparring.py with bots like other teams' (the CLAUDE.md example
bot, a calling station, a maniac). Pickle each to bots/<name>.pkl so
`python -m evals --opponents bots/<name>.pkl` plays them. Done when each
plays with no faults.

Commands (venv: `source .venv/bin/activate`):
python -m pytest tests/test_opponent.py -q ·
python -m pytest tests/test_model.py -q ·
python -m evals --opponents tight equity --deals 1000

Rules: plain-data attributes only (it is pickled), no os/open/eval/network,
under 1 ms per query. "Tested" names the command and its result. Stop and
ask the person before deleting anything or changing the contract.

When done: push the branch and tell your partner it is ready to merge.
