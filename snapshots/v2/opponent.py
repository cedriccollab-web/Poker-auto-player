"""
Per-team opponent statistics, learned from hands already played.

Owned by the opponents role (see AGENTS.md). The interface below is the
contract in docs/handoff/opponent-stats.md: model.py relies on these names,
arguments and return ranges, so change them only through that document.

Counts are reconstructed from the complete public action log. Priors
are retained when a statistic has no opportunities.

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
        self.hands = {}
        self.counts = {}
        self.chances = {}

    def update(self, hand_actions, game_state, my_id):
        """Learn transactionally from a completed hand; malformed input is ignored.

        Blinds are implicit, checks are not calls for aggression, VPIP is
        per hand, and shove opportunities are individual preflop decisions.
        No to-act-only queries or hidden engine fields are needed.
        """
        try:
            teams = tuple(game_state.teams)
            size = len(teams)
            if not 0 <= my_id < size:
                return
            bets = [0] * size
            small = game_state.button if size == 2 else (game_state.button + 1) % size
            big = (small + 1) % size
            # Forced short blinds cannot affect a later action by that seat:
            # a seat all-in from a blind never acts.
            bets[small] = game_state.small_blind
            bets[big] = game_state.big_blind
            current = max(bets)
            board = 0
            voluntary_wager = False
            events = []
            wins = [0] * size
            vpip = set()
            for action in hand_actions:
                seat, kind = action.player_id, action.kind
                if seat == -1 and kind == 'reveal_card':
                    board += 1
                    if board in (3, 4, 5):
                        bets = [0] * size
                        current = 0
                        voluntary_wager = False
                    continue
                if not 0 <= seat < size:
                    continue
                if kind == 'win':
                    wins[seat] += action.amount
                    continue
                if kind not in ('raise', 'call', 'fold'):
                    continue
                owed = max(0, current - bets[seat])
                facing = voluntary_wager and owed > 0
                paid = 0
                if kind == 'raise':
                    paid = action.amount - bets[seat]
                    bets[seat] = action.amount
                    current = max(current, action.amount)
                    voluntary_wager = True
                elif kind == 'call':
                    paid = owed
                    bets[seat] += paid
                if board == 0 and paid > 0:
                    vpip.add(seat)
                events.append((seat, kind, board == 0, facing, paid))

            counts = {seat: dict.fromkeys(PRIORS, 0) for seat in range(size) if seat != my_id}
            chances = {seat: dict.fromkeys(PRIORS, 0) for seat in counts}
            # Subtract payouts from the final stacks. A preflop raise was
            # all-in iff nothing remained and that seat spent nothing later.
            later_spending = set()
            for seat, kind, preflop, facing, paid in reversed(events):
                if seat in counts:
                    c, n = counts[seat], chances[seat]
                    if facing:
                        n['fold_to_raise'] += 1
                        c['fold_to_raise'] += int(kind == 'fold')
                    if kind == 'raise' or (kind == 'call' and paid > 0):
                        n['aggression'] += 1
                        c['aggression'] += int(kind == 'raise')
                    if preflop:
                        n['shove_rate'] += 1
                        if (kind == 'raise' and seat not in later_spending
                                and game_state.stacks[seat] - wins[seat] == 0):
                            c['shove_rate'] += 1
                if paid > 0:
                    later_spending.add(seat)
            for seat in counts:
                counts[seat]['vpip'] = int(seat in vpip)
                chances[seat]['vpip'] = 1
        except Exception:
            # Learning must never turn a valid poker hand into a bot fault.
            return
        for seat, c in counts.items():
            team = teams[seat]
            self.hands[team] = self.hands.get(team, 0) + 1
            previous = self.counts.setdefault(team, dict.fromkeys(PRIORS, 0))
            opportunities = self.chances.setdefault(team, dict.fromkeys(PRIORS, 0))
            for stat in PRIORS:
                previous[stat] += c[stat]
                opportunities[stat] += chances[seat][stat]

    def hands_seen(self, team):
        return self.hands.get(team, 0)

    def _query(self, team, stat):
        count = self.counts.get(team, {}).get(stat, 0)
        chances = self.chances.get(team, {}).get(stat, 0)
        if not chances:
            return PRIORS[stat]
        return (count + PRIORS[stat] * PRIOR_WEIGHT) / (chances + PRIOR_WEIGHT)

    def fold_to_raise(self, team):
        return self._query(team, 'fold_to_raise')

    def aggression(self, team):
        return self._query(team, 'aggression')

    def vpip(self, team):
        return self._query(team, 'vpip')

    def shove_rate(self, team):
        return self._query(team, 'shove_rate')
