
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
