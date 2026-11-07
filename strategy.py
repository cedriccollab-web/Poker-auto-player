"""
Strategy v4: heads-up no-limit hold'em at 25 big blinds.

Preflop: open most hands from the button, raise strong hands from the big
blind, and against a raise compare our equity against the raiser's likely
range (from opponent.py's stats; a shove is read as the team's own shove
rate) with the price. Postflop: Monte Carlo equity (equity.py) against that
range; after the opponent bets, their hand is weighted toward ones that have
something on this board. Bet for value, c-bet as the preflop raiser, call
when the equity beats the pot odds, otherwise fold. Per opponent: steal,
c-bet and bluff more against teams that fold; value-bet bigger and never
bluff against calling stations.
"""

import random

from card_utils import Card
from equity import PERCENTILE, card_int, equity, hand_class
from game_state import GameStateView
from opponent import OpponentStats
from player_action import DEALER, PlayerAction

# Module level, so it is not pickled with the model.
_rng = random.Random(20261107)

ITERS_PREFLOP = 300
ITERS_POSTFLOP = 300
# A preflop all-in is read as this strongest fraction of hands until the
# opponent's own shove rate has SHOVE_MIN_HANDS hands behind it.
SHOVE_RANGE = 0.50
SHOVE_MIN_HANDS = 20


class Model:
    def __init__(self):
        self.hand = []
        self.player_id = None
        # Learned across hands, per team (contract: docs/handoff/opponent-stats.md).
        self.opponents = OpponentStats()
        # Every action of the current hand, oldest first, for the tracker.
        self.hand_actions = []
        self.hole = []
        self.cls = ""

    def seed(self, hand: list[Card], player_id: int):
        self.hand = hand
        self.player_id = player_id
        self.hand_actions = []
        self.hole = [card_int(c) for c in hand]
        self.cls = hand_class(self.hole[0], self.hole[1])

    def run(
        self, actions: list[PlayerAction], game_state: GameStateView
    ) -> PlayerAction:
        self.hand_actions.extend(actions)
        try:
            return self._decide(game_state)
        except Exception:
            # Never fault: check when free, otherwise fold.
            if game_state.call_amount == 0:
                return PlayerAction.call(self.player_id)
            return PlayerAction.fold(self.player_id)

    def end_game(
        self, actions: list[PlayerAction], game_state: GameStateView
    ):
        self.hand_actions.extend(actions)
        try:
            self.opponents.update(self.hand_actions, game_state, self.player_id)
        except Exception:
            # A tracker bug must never fault the bot; it just learns less.
            pass

    # ------------------------------------------------------------------

    def _read_hand(self, opp):
        """From this hand's actions: the opponent's raises per street
        (0 preflop .. 3 river) and who raised last preflop."""
        street = 0
        board_cards = 0
        opp_raises = [0, 0, 0, 0]
        last_pre_raiser = None
        for a in self.hand_actions:
            if a.kind == "reveal_card" and a.player_id == DEALER:
                board_cards += 1
                street = 0 if board_cards < 3 else board_cards - 2
            elif a.kind == "raise":
                if a.player_id == opp:
                    opp_raises[street] += 1
                if street == 0:
                    last_pre_raiser = a.player_id
        return opp_raises, last_pre_raiser

    def _opp_range(self, gs, opp, team, opp_raises):
        """The strongest fraction of hands the opponent is likely to hold."""
        vpip = self.opponents.vpip(team)
        shove = self.opponents.shove_rate(team)
        if opp_raises[0] == 0:
            top = min(1.0, max(0.5, vpip + 0.25))
        else:
            top = min(1.0, max(0.15, vpip * 0.6))
            top *= 0.55 ** (opp_raises[0] - 1)
            if gs.street == "preflop" and gs.status(opp) == "all_in":
                # A team that shoves X% of its preflop decisions shoves
                # about its top X%. Until enough hands are seen, read a
                # shove as SHOVE_RANGE so shove-happy bots are not over-folded.
                if self.opponents.hands_seen(team) >= SHOVE_MIN_HANDS:
                    top = min(1.0, max(0.12, shove))
                else:
                    top = SHOVE_RANGE
        # Postflop bets are read on the board instead (see _bluff_weight).
        return max(0.04, top)

    def _bluff_weight(self, team, opp_raises):
        """None if the opponent has not bet or raised after the flop this
        hand; otherwise how much a hand with nothing on this board counts
        against hands with something: 0.30 at the prior aggression, up to
        0.90 for a maniac, down to 0.10 for a passive team."""
        if not any(opp_raises[1:]):
            return None
        aggr = self.opponents.aggression(team)
        return min(0.90, max(0.10, 0.30 + 1.5 * (aggr - 0.5)))

    def _profile(self, team):
        """How far the opponent leans calling station (0..1) or folder
        (0..1), from fold_to_raise. Both are 0 at the prior (0.40), so an
        unknown opponent gets exactly the v1 play."""
        ftr = self.opponents.fold_to_raise(team)
        station = min(1.0, max(0.0, (0.40 - ftr) / 0.30))
        folder = min(1.0, max(0.0, (ftr - 0.40) / 0.30))
        return station, folder

    def _raise(self, gs, total):
        me = self.player_id
        if not gs.can_raise:
            return PlayerAction.call(me)
        low, high = gs.raise_range
        total = int(total)
        chips = gs.stacks[me] + gs.bets[me]
        # Close to committed: go all-in rather than leave a stub.
        if total >= 0.45 * chips or high - total < 2 * gs.big_blind:
            total = high
        total = min(high, max(low, total))
        return PlayerAction.raise_to(me, total)

    def _decide(self, gs):
        me = self.player_id
        opp = 1 - me if gs.num_players == 2 else next(
            i for i in gs.players_in_hand if i != me)
        team = gs.teams[opp]
        bb = gs.big_blind
        to_call = gs.call_amount
        call = PlayerAction.call(me)
        fold = PlayerAction.fold(me)
        opp_raises, pre_raiser = self._read_hand(opp)
        station, folder = self._profile(team)

        if gs.street == "preflop":
            pct = PERCENTILE.get(self.cls, 1.0)
            if gs.current_bet <= bb:
                if to_call > 0:  # the button, first in: open wide
                    # Steal more from folders; raise only value into stations.
                    if pct <= 0.70 + 0.30 * folder - 0.15 * station:
                        size = 3.0 if station > 0.5 and pct <= 0.15 else 2.5
                        return self._raise(gs, size * bb)
                    if pct <= 0.90:
                        return call
                    return fold
                # Big blind after a limp.
                if pct <= 0.40 + 0.25 * folder - 0.10 * station:
                    return self._raise(gs, 3.5 * bb)
                return call
            top = self._opp_range(gs, opp, team, opp_raises)
            e = equity(self.hole, [], top, ITERS_PREFLOP, _rng)
            if e >= 0.60 and gs.can_raise:
                return self._raise(gs, 3 * gs.current_bet)
            if e >= gs.pot_odds + 0.02:
                return call
            return fold

        board = [card_int(c) for c in gs.board]
        top = self._opp_range(gs, opp, team, opp_raises)
        bluff = self._bluff_weight(team, opp_raises)
        e = equity(self.hole, board, top, ITERS_POSTFLOP, _rng, bluff=bluff)
        pot = gs.pot
        if to_call == 0:
            # Stations pay off: bet bigger and thinner for value.
            if e >= 0.72:
                return self._raise(gs, (0.75 + 0.35 * station) * pot)
            if e >= 0.58 - 0.08 * station:
                return self._raise(gs, (0.5 + 0.2 * station) * pot)
            # Folders give up: c-bet and bluff more; never bluff a station.
            cbet = 0.6 + 0.3 * folder - 0.5 * station
            if (gs.street == "flop" and pre_raiser == me
                    and _rng.random() < cbet):
                return self._raise(gs, 0.4 * pot)
            if (gs.street in ("turn", "river") and e < 0.3
                    and _rng.random() < 0.45 * folder):
                return self._raise(gs, 0.6 * pot)
            return call
        if e >= 0.80 and gs.can_raise:
            return self._raise(gs, gs.current_bet + pot)
        if e >= gs.pot_odds + 0.02:
            return call
        return fold
