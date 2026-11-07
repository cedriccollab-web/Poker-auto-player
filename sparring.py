"""Independent likely entrant styles. Pickles are built by the dev command.

"""
import random

from arena.dummies import EquityBot
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


class PushFold(CallingStation):
    """Shove the specified 28.8% of starting combinations; never limp."""
    def run(self, actions, game_state):
        if game_state.street != 'preflop':
            return PlayerAction.call(self.player_id)
        low, high = sorted(card.value for card in self.hand)
        play = (low == high or high == 14 or (high == 13 and low >= 9)
                or (high == 12 and low >= 10) or (high == 11 and low == 10))
        if play:
            return self._raise(game_state, game_state.max_raise_to)
        return PlayerAction.fold(self.player_id)


class Nit(CallingStation):
    """QQ+ and AK only; pot bets at every opportunity with those cards."""
    def run(self, actions, game_state):
        low, high = sorted(card.value for card in self.hand)
        play = (low == high and high >= 12) or (low == 13 and high == 14)
        if play:
            return self._raise(game_state, game_state.pot)
        if game_state.call_amount == 0:
            return PlayerAction.call(self.player_id)
        return PlayerAction.fold(self.player_id)


class PotBettor(CallingStation):
    """Bet the pot with a hole-card made pair+, call when facing a bet."""
    def run(self, actions, game_state):
        board = list(game_state.board)
        pair = self.hand[0].value == self.hand[1].value
        strong = pair
        if board:
            # Compare to every possible five-card hand available on the
            # board itself: a shared board pair is not our made hand.
            made = evaluate(self.hand + board)
            ranks = {c.value for c in board}
            connects = pair or any(c.value in ranks for c in self.hand)
            strong = made[0] >= 4 or (made[0] >= 1 and connects)
            if len(board) == 5:
                strong = strong and made > evaluate(board)
        if strong:
            if game_state.call_amount > 0:
                return PlayerAction.call(self.player_id)
            return self._raise(game_state, game_state.bets[self.player_id] + game_state.pot)
        if game_state.call_amount == 0:
            return PlayerAction.call(self.player_id)
        return PlayerAction.fold(self.player_id)


class MinRaiser(CallingStation):
    def run(self, actions, game_state):
        if game_state.can_raise:
            return self._raise(game_state, game_state.min_raise_to)
        return PlayerAction.call(self.player_id)


class Sharp(EquityBot):
    """Stock EquityBot policy with 400 samples and plain persistent data."""
    def __init__(self):
        self.hand = []
        self.player_id = None
        self.samples = 400
        self.random_state = random.Random(79).getstate()

    def run(self, actions, game_state):
        # Keep Random local; only its plain tuple state is pickled. The
        # delegated policy and evaluator are the unmodified EquityBot's.
        worker = EquityBot(seed=79, samples=self.samples)
        worker.hand = self.hand
        worker.player_id = self.player_id
        worker.rng.setstate(self.random_state)
        action = worker.run(actions, game_state)
        self.random_state = worker.rng.getstate()
        return action


class Bluffer(CallingStation):
    """See cheap flops, then pot-bluff with any cards and fold to aggression."""
    def run(self, actions, game_state):
        if game_state.street == 'preflop':
            if (game_state.call_amount == 0
                    or game_state.current_bet <= 3 * game_state.big_blind):
                return PlayerAction.call(self.player_id)
            return PlayerAction.fold(self.player_id)
        if game_state.call_amount > 0:
            return PlayerAction.fold(self.player_id)
        return self._raise(
            game_state, game_state.bets[self.player_id] + game_state.pot,
        )
