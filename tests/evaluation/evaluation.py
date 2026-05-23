"""
Evaluation utilities for chord recognition accuracy.

Functions:
  evaluate(test_cases, position_weights, key_prior_boost) -> (acc, wrong_cases)
  grid_search_1d(...) -> prints position_weights sweep
  grid_search_2d(...) -> prints 2D sweep over position_weights × key_prior_boost
  per_progression_breakdown(...) -> per-progression accuracy
"""

from whatthechord import harmony
from whatthechord.note import Note
from whatthechord.scale import Scale
from whatthechord.chord import Chord
from .progressions import ALL_TEST_CASES, PROGRESSIONS


def evaluate(test_cases, position_weights, key_prior_boost=None):
    """
    Returns (top-1 accuracy, list of wrongly-classified cases).

    Args:
        test_cases: list of (midi_notes, expected_root, expected_quality, key_args)
        position_weights: tuple, overrides default
        key_prior_boost: float, temporarily overrides module constant if not None
    """
    # Optionally override module-level key prior
    original_prior = harmony.KEY_PRIOR_BOOST
    if key_prior_boost is not None:
        harmony.KEY_PRIOR_BOOST = key_prior_boost

    try:
        correct = 0
        wrong_cases = []
        for midi_notes, expected_root, expected_quality, key_args in test_cases:
            chord = Chord([Note(n) for n in midi_notes])
            key = Scale.from_name(*key_args)
            results = harmony.analyze(
                chord, scale=key, position_weights=position_weights
            )
            if (results
                    and results[0].root == expected_root
                    and results[0].quality == expected_quality):
                correct += 1
            else:
                actual = results[0] if results else None
                wrong_cases.append((midi_notes, expected_root, expected_quality, actual))
        return correct / len(test_cases), wrong_cases
    finally:
        # Restore key prior to avoid leaking state
        harmony.KEY_PRIOR_BOOST = original_prior


def grid_search_1d(boosts=None):
    """Sweep position weight boost; key prior at default."""
    if boosts is None:
        boosts = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
    print(f"=== Position boost sweep ===")
    print(f"{'boost':>8} | {'top-1 acc':>10} | {'#wrong':>7}")
    print("-" * 35)
    for boost in boosts:
        weights = (1.0, boost, 1.0, boost)
        acc, wrong = evaluate(ALL_TEST_CASES, weights)
        print(f"{boost:>8.2f} | {acc:>9.2%} | {len(wrong):>7}")


def grid_search_2d(
    boosts=(1.0, 1.5, 1.75, 2.0),
    priors=(0.0, 0.1, 0.2, 0.3, 0.4),
):
    """Sweep both position boost and key prior boost."""
    print("=== 2D grid: position_boost × key_prior_boost ===\n")
    header = f"{'boost':>6} | " + " | ".join(f"prior={p:.2f}" for p in priors)
    print(header)
    print("-" * len(header))
    for boost in boosts:
        weights = (1.0, boost, 1.0, boost)
        row = [f"{boost:>6.2f}"]
        for prior in priors:
            acc, _ = evaluate(ALL_TEST_CASES, weights, key_prior_boost=prior)
            row.append(f"  {acc:.2%}")
        print(" | ".join(row))


def per_progression_breakdown(
    position_weights=(1.0, 1.75, 1.0, 1.75),
    key_prior_boost=None,
):
    """Per-progression accuracy. Reveals which chord types are weak."""
    print(f"=== Per-progression breakdown ===")
    print(f"  position_weights = {position_weights}")
    if key_prior_boost is not None:
        print(f"  key_prior_boost = {key_prior_boost}")
    print(f"\n{'Progression':<25} | {'Accuracy':>10} | {'N':>3}")
    print("-" * 50)
    for name, cases in PROGRESSIONS.items():
        acc, _ = evaluate(cases, position_weights, key_prior_boost)
        print(f"{name:<25} | {acc:>9.2%} | {len(cases):>3}")


def show_wrong_cases(
    position_weights=(1.0, 1.75, 1.0, 1.75),
    key_prior_boost=None,
):
    """Print incorrectly classified cases for error analysis."""
    _, wrong = evaluate(ALL_TEST_CASES, position_weights, key_prior_boost)
    if not wrong:
        print("All cases correctly classified.")
        return
    print(f"=== Wrong cases ({len(wrong)} of {len(ALL_TEST_CASES)}) ===")
    for midi, exp_root, exp_q, actual in wrong:
        actual_str = (
            f"{actual.root_name}{actual.quality} (c={actual.confidence:.2f})"
            if actual else "no match"
        )
        print(f"  notes={[Note(m) for m in midi]}")
        print(f"    expected: root_pc={exp_root}, quality={exp_q}")
        print(f"    actual:   {actual_str}")