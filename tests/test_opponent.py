import pickle
from types import SimpleNamespace

import pytest

from card_utils import Card, full_deck
from engine import play_hand
from opponent import OpponentStats, PRIORS, PRIOR_WEIGHT
from player_action import PlayerAction as A


def state(teams=('hero', 'villain'), stacks=(500, 500), button=0):
    return SimpleNamespace(teams=teams, stacks=stacks, button=button,
                           small_blind=10, big_blind=20)


def blend(stat, count, chances):
    return (count + PRIORS[stat] * PRIOR_WEIGHT) / (chances + PRIOR_WEIGHT)


@pytest.mark.parametrize('stat', PRIORS)
def test_unknown_and_unseen_priors(stat):
    tracker = OpponentStats()
    assert getattr(tracker, stat)('unknown') == PRIORS[stat]
    tracker.update([], state(), 0)
    assert getattr(tracker, stat)('villain') == (blend('vpip', 0, 1) if stat == 'vpip' else PRIORS[stat])
    assert tracker.hands_seen('unknown') == 0


def test_hands_and_seat_changes():
    tracker = OpponentStats()
    tracker.update([], state(), 0)
    tracker.update([], state(teams=('villain', 'hero')), 1)
    assert tracker.hands_seen('villain') == 2
    assert tracker.hands_seen('hero') == 0


def test_fold_to_raise_counts_only_facing_voluntary_wagers():
    tracker = OpponentStats()
    tracker.update([A.raise_to(0, 60), A.fold(1)], state(stacks=(520, 480)), 0)
    tracker.update([A.fold(0)], state(stacks=(490, 510)), 0)
    assert tracker.fold_to_raise('villain') == blend('fold_to_raise', 1, 1)
    tracker.update([A.raise_to(0, 60), A.call(1)], state(), 0)
    assert tracker.fold_to_raise('villain') == blend('fold_to_raise', 1, 2)


def test_aggression_excludes_checks_and_folds():
    tracker = OpponentStats()
    tracker.update([A.call(0), A.call(1)], state(), 0)  # BB checks
    assert tracker.aggression('villain') == PRIORS['aggression']
    tracker.update([A.raise_to(0, 60), A.raise_to(1, 160), A.call(0)], state(), 0)
    tracker.update([A.raise_to(0, 60), A.call(1)], state(), 0)
    assert tracker.aggression('villain') == blend('aggression', 1, 2)


def test_vpip_once_per_hand_and_no_blind_checks():
    tracker = OpponentStats()
    tracker.update([A.call(0), A.call(1)], state(), 0)
    assert tracker.vpip('villain') == blend('vpip', 0, 1)
    tracker.update([A.raise_to(0, 60), A.raise_to(1, 160), A.raise_to(0, 300),
                    A.call(1)], state(), 0)
    assert tracker.vpip('villain') == blend('vpip', 1, 2)
    # Small blind completing is voluntary; blinds are never in the action log.
    tracker.update([A.call(1), A.call(0)], state(button=1), 0)
    assert tracker.vpip('villain') == blend('vpip', 2, 3)


def test_preflop_shove_uses_unpaid_stack_not_payout():
    tracker = OpponentStats()
    tracker.update([A.raise_to(0, 60), A.raise_to(1, 500), A.fold(0), A.win(1, 560)],
                   state(stacks=(440, 560)), 0)
    assert tracker.shove_rate('villain') == blend('shove_rate', 1, 1)
    # A second action is a second preflop opportunity, not a second hand.
    tracker.update([A.raise_to(0, 60), A.raise_to(1, 140), A.raise_to(0, 500),
                    A.call(1)], state(stacks=(0, 0)), 0)
    assert tracker.shove_rate('villain') == blend('shove_rate', 1, 3)


def test_board_and_showdown_reveals_and_later_spending():
    flop = [A.reveal_card(Card.parse(c)) for c in ('AS', 'KH', '2D')]
    tracker = OpponentStats()
    actions = [A.call(0), A.raise_to(1, 100), A.call(0)] + flop
    actions += [A.raise_to(1, 400), A.call(0), A.reveal_card(Card.parse('QD'), 1)]
    tracker.update(actions, state(stacks=(0, 0)), 0)
    assert tracker.shove_rate('villain') == blend('shove_rate', 0, 1)
    assert tracker.vpip('villain') == blend('vpip', 1, 1)
    assert tracker.aggression('villain') == blend('aggression', 2, 2)


def test_pickling_retains_counts():
    tracker = OpponentStats()
    tracker.update([A.raise_to(0, 60), A.fold(1)], state(), 0)
    restored = pickle.loads(pickle.dumps(tracker))
    assert restored.fold_to_raise('villain') == blend('fold_to_raise', 1, 1)
    assert restored.hands_seen('villain') == 1


def test_bad_input_never_raises_or_partially_updates():
    tracker = OpponentStats()
    tracker.update(None, None, 0)
    tracker.update([object()], state(), 0)
    assert tracker.hands_seen('villain') == 0


def test_real_engine_payout_and_short_stack_shove():
    from arena.dummies import ShoveBot, CallBot
    tracker = OpponentStats()
    result = play_hand([CallBot(), ShoveBot()], full_deck(), [500, 60], teams=['hero', 'villain'])
    final = state(stacks=tuple(s + net for s, net in zip((500, 60), result.net)))
    tracker.update(result.actions, final, 0)
    assert tracker.shove_rate('villain') == blend('shove_rate', 1, 1)
    assert tracker.hands_seen('villain') == 1


@pytest.mark.parametrize('name', ['example', 'station', 'maniac'])
def test_sparring_pickles_play_without_faults(name):
    from arena.match import MatchConfig, play_match
    from arena.players import player
    result = play_match([player('bots/' + name + '.pkl'), player('random')],
                        MatchConfig(deals=30, seed=47))
    from evals.score import score
    measured = score([result])
    assert measured.faults == [0, 0] or measured.faults == (0, 0)


@pytest.mark.parametrize('name', ['pushfold', 'nit', 'potbettor', 'minraiser', 'sharp'])
def test_hard_sparring_pickles_play_legally(name):
    from arena.match import MatchConfig, play_match
    from arena.players import player
    from evals.score import score
    # Both normal and short stacks exercise raise caps and all-in calls.
    for stack in (500, 60):
        result = score([play_match(
            [player('bots/' + name + '.pkl'), player('random')],
            MatchConfig(deals=10, seed=79, stack=stack),
        )])
        assert tuple(result.faults) == (0, 0), result.first_faults
