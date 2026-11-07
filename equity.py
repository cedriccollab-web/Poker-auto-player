"""
Fast hand strength for the strategy role (see AGENTS.md).

Cards are ints 0..51: (value - 2) * 4 + suit index. `score7` ranks 5 to 7
cards as one int that compares like card_utils.evaluate (higher wins, equal
splits) but runs several times faster, so the bot can simulate hundreds of
showdowns per decision. tests/test_strategy.py checks it against
card_utils.evaluate.
"""

from preflop_table import PRE_EQ

SUITS = "CDHS"
RANKS = "23456789TJQKA"
TOTAL_COMBOS = 1326


def card_int(card):
    return (card.value - 2) * 4 + SUITS.index(card.suit)


def _build_tables():
    pop = [0] * 8192
    straight = [-1] * 8192
    top5 = [0] * 8192
    for m in range(8192):
        pop[m] = bin(m).count("1")
        # Bit 0 is the ace played low, bit r + 1 is rank r.
        ext = (m << 1) | ((m >> 12) & 1)
        for hi in range(13, 3, -1):
            if (ext >> (hi - 4)) & 31 == 31:
                straight[m] = hi - 1
                break
        packed, n = 0, 0
        for r in range(12, -1, -1):
            if (m >> r) & 1:
                packed |= r << (16 - 4 * n)
                n += 1
                if n == 5:
                    break
        top5[m] = packed
    return pop, straight, top5


_POP, _STRAIGHT, _TOP5 = _build_tables()


def score7(cards):
    """Rank 5 to 7 card ints: category << 20 | tie-breakers."""
    rc = [0] * 13
    sm = [0, 0, 0, 0]
    allm = 0
    for c in cards:
        r = c >> 2
        rc[r] += 1
        b = 1 << r
        sm[c & 3] |= b
        allm |= b
    flush = 0
    for m in sm:
        if _POP[m] >= 5:
            flush = m
            break
    if flush:
        s = _STRAIGHT[flush]
        if s >= 0:
            return 0x800000 | s
    quad = trip1 = trip2 = pair1 = pair2 = -1
    for r in range(12, -1, -1):
        n = rc[r]
        if n < 2:
            continue
        if n == 4:
            quad = r
        elif n == 3:
            if trip1 < 0:
                trip1 = r
            elif trip2 < 0:
                trip2 = r
        elif pair1 < 0:
            pair1 = r
        elif pair2 < 0:
            pair2 = r
    if quad >= 0:
        return 0x700000 | quad << 16 | (_TOP5[allm & ~(1 << quad)] >> 16) << 12
    if trip1 >= 0 and (trip2 >= 0 or pair1 >= 0):
        return 0x600000 | trip1 << 16 | max(trip2, pair1) << 12
    if flush:
        return 0x500000 | _TOP5[flush]
    s = _STRAIGHT[allm]
    if s >= 0:
        return 0x400000 | s
    if trip1 >= 0:
        return 0x300000 | trip1 << 16 | (_TOP5[allm & ~(1 << trip1)] >> 12) << 8
    if pair2 >= 0:
        rest = allm & ~(1 << pair1) & ~(1 << pair2)
        return 0x200000 | pair1 << 16 | pair2 << 12 | (_TOP5[rest] >> 16) << 8
    if pair1 >= 0:
        return 0x100000 | pair1 << 16 | (_TOP5[allm & ~(1 << pair1)] >> 8) << 4
    return _TOP5[allm]


def hand_class(a, b):
    """'AA', 'AKs' or 'AKo' for two card ints."""
    r1, r2 = a >> 2, b >> 2
    if r1 < r2:
        r1, r2 = r2, r1
    if r1 == r2:
        return RANKS[r1] * 2
    return RANKS[r1] + RANKS[r2] + ("s" if (a & 3) == (b & 3) else "o")


CLASS_COMBOS = {}
for _a in range(52):
    for _b in range(_a + 1, 52):
        CLASS_COMBOS.setdefault(hand_class(_a, _b), []).append((_a, _b))

# Strongest first, by equity against a random hand.
CLASS_ORDER = sorted(CLASS_COMBOS, key=lambda k: -PRE_EQ.get(k, 0.5))

# Fraction of all combos at least as strong as each class: 0 best, 1 worst.
PERCENTILE = {}
_seen = 0
for _k in CLASS_ORDER:
    _seen += len(CLASS_COMBOS[_k])
    PERCENTILE[_k] = _seen / TOTAL_COMBOS

_RANGE_CACHE = {}


def range_combos(top):
    """Every combo in the strongest `top` fraction of hands (0 < top <= 1)."""
    key = round(min(1.0, max(0.02, top)), 2)
    combos = _RANGE_CACHE.get(key)
    if combos is None:
        combos = []
        for k in CLASS_ORDER:
            combos.extend(CLASS_COMBOS[k])
            if len(combos) >= key * TOTAL_COMBOS:
                break
        _RANGE_CACHE[key] = combos
    return combos


def equity(hole, board, top, iters, rng):
    """
    Share of the pot won by `hole` (two card ints) on `board` (0 to 5 card
    ints) against one opponent holding a hand from the strongest `top`
    fraction of starting hands, over `iters` random run-outs. Ties count
    half.
    """
    dead = set(hole) | set(board)
    combos = [c for c in range_combos(top) if c[0] not in dead and c[1] not in dead]
    if not combos:
        combos = [c for c in range_combos(1.0) if c[0] not in dead and c[1] not in dead]
    deck = [c for c in range(52) if c not in dead]
    need = 5 - len(board)
    n = len(combos)
    won = 0.0
    for _ in range(iters):
        o1, o2 = combos[int(rng.random() * n)]
        if need:
            drawn = rng.sample(deck, need + 2)
            run = [c for c in drawn if c != o1 and c != o2][:need]
            full = board + run
        else:
            full = board
        mine = score7(hole + full)
        theirs = score7([o1, o2] + full)
        if mine > theirs:
            won += 1.0
        elif mine == theirs:
            won += 0.5
    return won / iters
