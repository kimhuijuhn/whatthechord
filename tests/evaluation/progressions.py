"""
Labeled chord progressions for accuracy evaluation.

Each entry: (midi_notes, expected_root_pc, expected_quality, scale_context)

The test set is intentionally designed to exercise hyperparameters:
  - Complete chord progressions: boost-insensitive (sanity check)
  - Incomplete chords (shell voicings, power chords): boost-sensitive
  - Inversions: verify inversion detection
  - Borrowed chords: minor key V (e.g., E in A minor)
"""

# =============================================================================
# Complete chord progressions (boost-insensitive sanity check)
# =============================================================================

I_IV_V_I_C_MAJOR = [
    ([60, 64, 67],     0, "maj", ("C", "major")),   # C major (I)
    ([65, 69, 60],     5, "maj", ("C", "major")),   # F major (IV)
    ([67, 71, 62],     7, "maj", ("C", "major")),   # G major (V)
    ([60, 64, 67],     0, "maj", ("C", "major")),   # C major (I)
]

II_V_I_C_MAJOR = [
    ([62, 65, 69],     2, "min", ("C", "major")),   # Dm (ii)
    ([67, 71, 62, 65], 7, "7",   ("C", "major")),   # G7 (V7)
    ([60, 64, 67, 71], 0, "maj7",("C", "major")),   # Cmaj7 (I7)
]

I_IV_V_A_MINOR = [
    ([57, 60, 64],     9, "min", ("A", "minor")),   # Am (i)
    ([62, 65, 69],     2, "min", ("A", "minor")),   # Dm (iv)
    ([64, 68, 71],     4, "maj", ("A", "minor")),   # E (V borrowed from harmonic minor)
]

VI_IV_I_V_G_MAJOR = [
    ([64, 67, 71],     4, "min", ("G", "major")),   # Em (vi)
    ([60, 64, 67],     0, "maj", ("G", "major")),   # C (IV)
    ([67, 71, 62],     7, "maj", ("G", "major")),   # G (I)
    ([62, 66, 69],     2, "maj", ("G", "major")),   # D (V)
]

# =============================================================================
# Incomplete chords (boost-sensitive — main grid search workload)
# =============================================================================

# Shell voicings: 3rd + 7th only (root omitted by convention)
SHELL_VOICINGS = [
    ([64, 70],   0, "7",    ("C", "major")),   # E + Bb = C7 (shell)
    ([66, 72],   2, "7",    ("G", "major")),   # F# + C = D7 (shell)
    ([71, 65],   7, "7",    ("C", "major")),   # B + F = G7 (shell)
    ([69, 64],   5, "maj7", ("F", "major")),   # A + E = Fmaj7 (shell)
]

# Power chords (root + 5th, no 3rd → ambiguous between maj/min)
POWER_CHORDS = [
    ([60, 67],   0, "maj", ("C", "major")),   # C5 in C major → I
    ([69, 64],   9, "min", ("A", "minor")),   # A5 in A minor → i
    ([67, 62],   7, "maj", ("G", "major")),   # G5 in G major → I
    ([62, 69],   2, "min", ("C", "major")),   # D5 in C major → ii
]

# 7th chords with 3rd omitted
NO_THIRD_SEVENTHS = [
    ([60, 67, 70],   0, "7",    ("C", "major")),   # C-G-Bb → C7 (no 3rd)
    ([62, 69, 72],   2, "min7", ("C", "major")),   # D-A-C → Dm7 (no 3rd)
]

# =============================================================================
# Inversions
# =============================================================================

INVERSIONS = [
    ([64, 67, 72],     0, "maj", ("C", "major")),   # E-G-C: C/E (1st)
    ([67, 72, 76],     0, "maj", ("C", "major")),   # G-C-E: C/G (2nd)
    ([58, 60, 64, 67], 0, "7",   ("C", "major")),   # Bb-C-E-G: C7/Bb (3rd)
    ([60, 64, 69],     9, "min", ("A", "minor")),   # C-E-A: Am/C (1st)
]

# =============================================================================
# Combined access
# =============================================================================

PROGRESSIONS = {
    "I-IV-V-I (C major)":   I_IV_V_I_C_MAJOR,
    "ii-V-I (C major)":     II_V_I_C_MAJOR,
    "i-iv-V (A minor)":     I_IV_V_A_MINOR,
    "vi-IV-I-V (G major)":  VI_IV_I_V_G_MAJOR,
    "Shell voicings":       SHELL_VOICINGS,
    "Power chords":         POWER_CHORDS,
    "No-3rd 7ths":          NO_THIRD_SEVENTHS,
    "Inversions":           INVERSIONS,
}

ALL_TEST_CASES = [tc for tcs in PROGRESSIONS.values() for tc in tcs]