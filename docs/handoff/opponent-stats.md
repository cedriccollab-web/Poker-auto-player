# Handoff: opponent statistics

**From:** strategy · **To:** opponents · **Date:** 2026-11-07 · **Status:** agreed

## What the bot needs

`model.py` adjusts its play per opponent once it has seen enough hands with
them: bluff more against teams that fold to raises, call wider against teams
that shove often, value-bet thinner against teams that call everything. It
needs a few numbers per team, cheap to read on every turn.

## Contract

`opponent.py`, class `OpponentStats`, built with no arguments in
`Model.__init__` and pickled inside the model (plain data only).

- `update(hand_actions, game_state, my_id) -> None`: once per hand, from
  `Model.end_game`. `hand_actions` is every `PlayerAction` of the hand,
  oldest first (every `run` call's actions, then `end_game`'s). Never raises.
- `hands_seen(team) -> int`
- `fold_to_raise(team) -> float`: P(fold | facing a bet or raise). Prior 0.40.
- `aggression(team) -> float`: (bets + raises) / (bets + raises + calls).
  Prior 0.50.
- `vpip(team) -> float`: P(chips in voluntarily preflop; the big blind
  checking does not count). Prior 0.60.
- `shove_rate(team) -> float`: P(raise all-in preflop | they act preflop).
  Prior 0.05.

Every query: a float in [0, 1]; for a team with no hands, exactly its prior;
otherwise `(count + prior * PRIOR_WEIGHT) / (chances + PRIOR_WEIGHT)` so a
few hands move it only a little. Under 1 ms per call. Unknown team names are
not an error.

The stub in `opponent.py` honours all of this with priors only, so
`model.py` is built against it now.

## Facts the counting must respect

- Blinds are posted by the engine. Check `engine.py` for whether they appear
  as actions before counting them as raises or calls.
- Board cards are `reveal_card` with `player_id == DEALER` (-1): the 3rd,
  4th and 5th open the flop, turn and river. Use them to know the street.
- A `raise` amount is the street total, not the increment. All-in means the
  total used the player's whole stack.
- In the real round the same model plays one opponent for 200 hands per
  seat rotation, then is rebuilt from the pickle: learning starts at zero
  each rotation.

## Tests the opponents role will add

- L1 `tests/test_opponent.py`: hand-built action lists for each stat, the
  prior with no hands, the blend after a few, unknown teams, pickling. Each
  new test shown red once (break the count, see it fail, restore).
