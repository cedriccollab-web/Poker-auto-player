"""Independent likely entrant styles. Pickles are built by the dev command.

"""
from card_utils import evaluate
from player_action import PlayerAction


class CallingStation:
    def __init__(self):
        self.hand = []
        self.player_id = None

    def seed(self, hand, player_id):
        self.hand = list(hand)
        self.player_id = player_id

    def run(self, actions, game_state):
        return PlayerAction.call(self.player_id)

    def _raise(self, state, total):
        if not state.can_raise:
            return PlayerAction.call(self.player_id)
        low, high = state.raise_range
        return PlayerAction.raise_to(self.player_id, int(min(high, max(low, total))))


class ExampleBot(CallingStation):
    """The example policy in CLAUDE.md, including its board-pair weakness."""
    def run(self, actions, game_state):
        if len(game_state.board) >= 3:
            strong = evaluate(self.hand + list(game_state.board))[0] >= 2
        else:
            high, low = sorted(card.value for card in self.hand)[::-1]
            strong = high == low or low >= 10
        if strong and game_state.can_raise:
            return self._raise(game_state, game_state.pot)
        if game_state.call_amount == 0 or game_state.pot_odds < 0.25:
            return PlayerAction.call(self.player_id)
        return PlayerAction.fold(self.player_id)


class Maniac(CallingStation):
    """Raises 80% of decisions, sometimes shoves; almost never folds."""
    def __init__(self):
        super().__init__()
        self.random_state = 16381

    def run(self, actions, game_state):
        self.random_state = (1664525 * self.random_state + 1013904223) % 2**32
        roll = self.random_state / 2**32
        if roll < 0.8 and game_state.can_raise:
            target = (game_state.max_raise_to if roll < 0.15 else
                      game_state.bets[self.player_id] + game_state.call_amount
                      + game_state.pot + game_state.call_amount)
            return self._raise(game_state, target)
        return PlayerAction.call(self.player_id)
