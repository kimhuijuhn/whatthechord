# test_progressions.py
"""
Labeled chord progressions for accuracy evaluation.
Each entry: (note_set, expected_root_pc, expected_quality, scale_context)
"""

PROGRESSIONS = {
    "C_MAJOR_PROGRESSIONS": [
        ([60, 64, 67],     0, "maj", ("C", "major")),   # C major (I)
        ([65, 69, 60],     5, "maj", ("C", "major")),   # F major (IV)
        ([67, 71, 62],     7, "maj", ("C", "major")),   # G major (V)
        ([60, 64, 67],     0, "maj", ("C", "major")),   # C major (I)
    ],

    # ii-V-I in C major
    "II_V_I_C": [
        ([62, 65, 69],     2, "min", ("C", "major")),   # Dm (ii)
        ([67, 71, 62, 65], 7, "7",   ("C", "major")),   # G7 (V7)
        ([60, 64, 67, 71], 0, "maj7",("C", "major")),   # Cmaj7 (I)
    ],

    # i-iv-V in A natural minor
    "I_IV_V_A_MINOR": [
        ([57, 60, 64],     9, "min", ("A", "minor")),   # Am (i)
        ([62, 65, 69],     2, "min", ("A", "minor")),   # Dm (iv)
        ([64, 68, 71],     4, "maj", ("A", "minor")),   # E (V borrowed!)
    ]
}

ALL_TEST_CASES = [tc for tcs in PROGRESSIONS.values() for tc in tcs]