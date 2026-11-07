Development sparring opponents (not the team submission)

example.pkl: CLAUDE.md's example strategy, including its board-pair weakness.
station.pkl: checks and calls every hand.
maniac.pkl: raises 80% of decisions when allowed, sometimes all-in.
pushfold.pkl: shoves any pair, any ace, K9+, QT+, JT (28.81% of combos).
nit.pkl: QQ+ and AK only; raises to the pot every street, else check/folds.
potbettor.pkl: bets pot with a hole-card pair or better; calls bets with it.
minraiser.pkl: min-raises whenever legal, otherwise calls.
sharp.pkl: EquityBot subclass, 400 samples; stock policy and evaluator.
bluffer.pkl: calls preflop totals up to 3 BB, folds to bigger raises; bets
  pot whenever postflop call_amount is zero, folds to bets/raises. No card
  strength filter. Checks when raising is unavailable.
Sharp retains only plain RNG state, using a local EquityBot per decision;
its RNG starts from seed 79 and continues across hands.

All classes live in the root sparring.py. Keep that file on the import path.
Each pickle uses protocol 4 and holds plain data only.

Play:
.venv/bin/python -m evals --opponents bots/example.pkl bots/station.pkl bots/maniac.pkl --deals 1000

Rebuild from the repository root:
.venv/bin/python - <<'PY'
import pickle
from pathlib import Path
from sparring import ExampleBot, CallingStation, Maniac, PushFold, Nit, PotBettor, MinRaiser, Sharp, Bluffer
for name, cls in [('example', ExampleBot), ('station', CallingStation), ('maniac', Maniac),
                  ('pushfold', PushFold), ('nit', Nit), ('potbettor', PotBettor),
                  ('minraiser', MinRaiser), ('sharp', Sharp), ('bluffer', Bluffer)]:
    Path('bots', name + '.pkl').write_bytes(pickle.dumps(cls(), protocol=4))
PY
