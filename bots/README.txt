Development sparring opponents (not the team submission)

example.pkl: CLAUDE.md's example strategy, including its board-pair weakness.
station.pkl: checks and calls every hand.
maniac.pkl: raises 80% of decisions when allowed, sometimes all-in.

All classes live in the root sparring.py. Keep that file on the import path.
Each pickle uses protocol 4 and holds plain data only.

Play:
.venv/bin/python -m evals --opponents bots/example.pkl bots/station.pkl bots/maniac.pkl --deals 1000

Rebuild from the repository root:
.venv/bin/python - <<'PY'
import pickle
from pathlib import Path
from sparring import ExampleBot, CallingStation, Maniac
for name, cls in [('example', ExampleBot), ('station', CallingStation), ('maniac', Maniac)]:
    Path('bots', name + '.pkl').write_bytes(pickle.dumps(cls(), protocol=4))
PY
