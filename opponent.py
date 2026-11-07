"""
Per-team opponent statistics, learned from hands already played.

Owned by the opponents role (see AGENTS.md). The interface below is the
contract in docs/handoff/opponent-stats.md: model.py relies on these names,
arguments and return ranges, so change them only through that document.

STUB: every query returns its prior until the real counting lands. The
priors are what a query must return for a team with no hands seen.

The object is pickled inside Model, so it holds plain data only (dicts of
numbers). No imports beyond the repo's own modules and the standard
library's pure helpers; no os, files, threads or lambdas.
"""

# A query blends what was seen with its prior, weighted as this many hands.
PRIOR_WEIGHT = 10

PRIORS = {
    "fold_to_raise": 0.40,  # P(they fold | facing a bet or raise)
    "aggression": 0.50,     # (bets + raises) / (bets + raises + calls)
    "vpip": 0.60,           # P(they put chips in voluntarily preflop)
    "shove_rate": 0.05,     # P(they raise all-in preflop | they act preflop)
}


class OpponentStats:
    def __init__(self):
        # team name -> hands seen with that team at the table
        self.hands = {}

    def update(self, hand_actions, game_state, my_id):
        """
        Learn from one finished hand. Called once per hand, from
        Model.end_game.

        hand_actions: every PlayerAction of the hand, oldest first: each
            run() call's actions, then end_game's, joined. Board cards are
            reveal_card with player_id == DEALER (-1); showdown cards are
            reveal_card with the player's own id; then one win per winner.
        game_state: the final GameStateView (stacks after the pot).
        my_id: our seat this hand. Opponents are the other seats; their
            team is game_state.teams[seat].
        """
        for seat, team in enumerate(game_state.teams):
            if seat != my_id:
                self.hands[team] = self.hands.get(team, 0) + 1

    def hands_seen(self, team):
        return self.hands.get(team, 0)

    def fold_to_raise(self, team):
        return PRIORS["fold_to_raise"]

    def aggression(self, team):
        return PRIORS["aggression"]

    def vpip(self, team):
        return PRIORS["vpip"]

    def shove_rate(self, team):
        return PRIORS["shove_rate"]
