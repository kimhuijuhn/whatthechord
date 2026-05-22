from src import harmony
from src.Note import Note
from src.Scale import Scale
from src.Chord import Chord
from progressions import PROGRESSIONS

def evaluate(test_cases, position_weights):
    """Returns top-1 accuracy."""
    harmony.POSITION_WEIGHTS = position_weights  # override hyperparameter
    correct = 0
    for midi_notes, expected_root, expected_quality, key_args in test_cases:
        chord = Chord([Note(n) for n in midi_notes])
        key = Scale.from_name(*key_args)
        results = harmony.analyze(chord, scale=key)
        if results and results[0].root == expected_root and results[0].quality == expected_quality:
            correct += 1
    return correct / len(test_cases)

def grid_search():
    """Sweep 3rd/7th boost from 1.0 to 2.5."""
    print(f"{'Boost':>8} | {'Accuracy':>10}")
    print("-" * 23)
    for boost in [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]:
        weights = (1.0, boost, 1.0, boost)
        acc = evaluate(ALL_TEST_CASES, weights)
        print(f"{boost:>8.2f} | {acc:>9.2%}")