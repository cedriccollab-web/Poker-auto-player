"""L1 checks for the strategy role's equity.py (fast evaluator, equity)."""

import random

import pytest

import equity as eq
from card_utils import evaluate, full_deck


DECK = full_deck()
INTS = [eq.card_int(c) for c in DECK]


def _sign(x):
    return (x > 0) - (x < 0)


@pytest.mark.parametrize("n", [5, 6, 7])
def test_score7_orders_hands_like_the_official_evaluator(n):
    rng = random.Random(n)
    for _ in range(3000):
        idx = rng.sample(range(52), 2 * n)
        a, b = idx[:n], idx[n:]
        ra = evaluate([DECK[i] for i in a])
        rb = evaluate([DECK[i] for i in b])
        sa = eq.score7([INTS[i] for i in a])
        sb = eq.score7([INTS[i] for i in b])
        assert sa >> 20 == ra[0], [str(DECK[i]) for i in a]
        assert _sign(sa - sb) == _sign((ra > rb) - (ra < rb)), (
            [str(DECK[i]) for i in a], [str(DECK[i]) for i in b])


EDGE_HANDS = {
    "full house with four to a flush": ("AS KS 9S 2S AH AD KD", 6),
    "flush and straight, not a straight flush": ("9S 8S 7S 2S 6H 5D KS", 5),
    "wheel straight": ("AS 2D 3C 4H 5S 9D KC", 4),
    "wheel straight flush": ("AH 2H 3H 4H 5H KD KC", 8),
    "two trips make a full house": ("7S 7D 7C 4H 4S 4D 2C", 6),
    "three pairs are two pair": ("QS QD 9C 9H 5S 5D 2C", 2),
    "quads with a pair on board": ("8S 8D 8C 8H KS KD 2C", 7),
    "six-card straight takes the top": ("4S 5D 6C 7H 8S 9D KC", 4),
}


@pytest.mark.parametrize("name", EDGE_HANDS)
def test_score7_edge_hands_match_the_official_evaluator(name):
    from card_utils import Card
    text, category = EDGE_HANDS[name]
    cards = [Card.parse(t) for t in text.split()]
    assert eq.score7([eq.card_int(c) for c in cards]) >> 20 == category
    assert evaluate(cards)[0] == category


def test_score7_edge_hands_order_against_each_other():
    from card_utils import Card
    hands = [[Card.parse(t) for t in text.split()] for text, _ in EDGE_HANDS.values()]
    for a in hands:
        for b in hands:
            ra, rb = evaluate(a), evaluate(b)
            sa = eq.score7([eq.card_int(c) for c in a])
            sb = eq.score7([eq.card_int(c) for c in b])
            assert _sign(sa - sb) == _sign((ra > rb) - (ra < rb))


def test_score7_shared_board_ties_and_kickers():
    # Same board, both players play it: a split.
    board = [eq.card_int(c) for c in (DECK[48], DECK[44], DECK[40], DECK[36], DECK[32])]
    assert eq.score7(board + [0, 5]) == eq.score7(board + [1, 4])
    rng = random.Random(7)
    for _ in range(3000):
        idx = rng.sample(range(52), 9)
        shared = idx[4:]
        a, b = idx[:2] + shared, idx[2:4] + shared
        ra = evaluate([DECK[i] for i in a])
        rb = evaluate([DECK[i] for i in b])
        sa = eq.score7([INTS[i] for i in a])
        sb = eq.score7([INTS[i] for i in b])
        assert _sign(sa - sb) == _sign((ra > rb) - (ra < rb))


def test_preflop_table_covers_every_class_strongest_first():
    assert len(eq.PRE_EQ) == 169
    assert eq.CLASS_ORDER[0] == "AA"
    assert eq.PRE_EQ["AA"] > eq.PRE_EQ["AKs"] > eq.PRE_EQ["72o"]
    assert sum(len(v) for v in eq.CLASS_COMBOS.values()) == 1326
    assert eq.PERCENTILE["AA"] == pytest.approx(6 / 1326)
    assert eq.PERCENTILE[eq.CLASS_ORDER[-1]] == 1.0


def test_range_combos_take_the_strongest_fraction():
    assert len(eq.range_combos(1.0)) == 1326
    top10 = eq.range_combos(0.10)
    assert 0.10 * 1326 <= len(top10) < 0.14 * 1326
    assert {eq.hand_class(a, b) for a, b in top10} >= {"AA", "KK", "AKs"}


def test_equity_against_random_and_against_a_strong_range():
    rng = random.Random(3)
    aces = [eq.card_int(DECK[48]), eq.card_int(DECK[49])]
    seven_deuce = [eq.card_int(DECK[20]), eq.card_int(DECK[1])]
    assert eq.equity(aces, [], 1.0, 4000, rng) == pytest.approx(0.852, abs=0.02)
    assert eq.equity(seven_deuce, [], 1.0, 4000, rng) < 0.40
    # Against only the top 5% of hands (mostly big pairs), AK offsuit goes
    # from a favourite to an underdog.
    ace_king = [eq.card_int(DECK[48]), eq.card_int(DECK[45])]  # AC KD
    assert eq.equity(ace_king, [], 1.0, 4000, rng) > 0.60
    assert eq.equity(ace_king, [], 0.05, 4000, rng) < 0.50


def test_equity_on_the_river_is_exact_against_one_hand():
    rng = random.Random(4)
    # Royal flush on board for us is impossible to beat: always 1.0 or a tie.
    hole = [eq.card_int(DECK[51]), eq.card_int(DECK[47])]  # AS KS
    board = [eq.card_int(DECK[i]) for i in (43, 39, 35, 0, 1)]  # QS JS TS 2C 2D
    assert eq.equity(hole, board, 1.0, 500, rng) == 1.0


class _FixedStats:
    """Stands in for OpponentStats with a fixed fold_to_raise."""

    def __init__(self, ftr):
        self.ftr = ftr

    def fold_to_raise(self, team):
        return self.ftr


@pytest.mark.parametrize("ftr, station, folder", [
    (0.40, 0.0, 0.0),   # the prior: an unknown opponent gets v1's play
    (0.05, 1.0, 0.0),   # calls everything
    (0.25, 0.5, 0.0),
    (0.55, 0.0, 0.5),
    (0.85, 0.0, 1.0),   # folds to most bets
])
def test_profile_reads_stations_and_folders_from_fold_to_raise(ftr, station, folder):
    from model import Model
    m = Model()
    m.opponents = _FixedStats(ftr)
    s, f = m._profile("anyone")
    assert s == pytest.approx(station)
    assert f == pytest.approx(folder)


def test_profile_at_the_real_prior_is_neutral():
    from model import Model
    assert Model()._profile("never seen") == (0.0, 0.0)


class _ShoveStats:
    """Fixed opponent stats for reading a preflop shove."""

    def __init__(self, shove, hands):
        self.shove, self.hands = shove, hands

    def vpip(self, team):
        return 0.6

    def aggression(self, team):
        return 0.5

    def shove_rate(self, team):
        return self.shove

    def hands_seen(self, team):
        return self.hands

    def fold_to_raise(self, team):
        return 0.4


class _AllInPreflop:
    street = "preflop"

    def status(self, seat):
        return "all_in"


@pytest.mark.parametrize("shove, hands, expected", [
    (0.29, 50, 0.29),   # a tight shover is read as its own shove rate
    (0.95, 50, 0.95),   # a bot that shoves everything is wide
    (0.02, 50, 0.12),   # never read narrower than the top 12%
    (0.29, 5, None),    # too few hands seen: the default SHOVE_RANGE
])
def test_a_preflop_shove_is_read_as_the_teams_shove_rate(shove, hands, expected):
    import model
    m = model.Model()
    m.opponents = _ShoveStats(shove, hands)
    top = m._opp_range(_AllInPreflop(), 1, "them", [1, 0, 0, 0])
    assert top == pytest.approx(model.SHOVE_RANGE if expected is None else expected)


def _ints(text):
    from card_utils import Card
    return [eq.card_int(Card.parse(t)) for t in text.split()]


@pytest.mark.parametrize("hole, board, expected", [
    ("7H 6H", "KS 7D 2C", True),         # pair using a hole card
    ("QH JD", "KS 7D 2C", False),        # nothing
    ("AH 3H", "KH 7H 2C", True),         # flush draw with a hole card
    ("AH 3H", "KH 7H 2C 9S 4D", False),  # the draw missed on the river
    ("QH JD", "KS KD 2C", False),        # only the board's pair
    ("2H 2D", "KS KD 9C", True),         # two pair with a pocket pair
])
def test_has_something_after_the_flop(hole, board, expected):
    assert eq.has_something(_ints(hole), _ints(board)) is expected


def test_equity_against_a_postflop_bet_counts_mostly_made_hands():
    rng = random.Random(5)
    hole, board = _ints("AH 5C"), _ints("KS 7D 2C 9S 4H")  # ace high on the river
    plain = eq.equity(hole, board, 1.0, 3000, rng)
    honest = eq.equity(hole, board, 1.0, 3000, rng, bluff=0.1)
    anything = eq.equity(hole, board, 1.0, 3000, rng, bluff=1.0)
    assert honest < plain - 0.15
    assert anything == pytest.approx(plain, abs=0.04)
