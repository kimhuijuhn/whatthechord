"""
Jazz standard lead sheets as Score instances.

These serve as reference progressions for ScoreFollower demos and tests.
Each entry is a real jazz standard transcribed from common Real Book
sources.

Conventions:
  - Chord spellings use flats (Eb, Bb, Ab) — jazz Real Book convention
  - Multi-chord bars expressed via from_bars() with space-separated symbols
  - Tempo and time signature reflect typical performance practice
"""

from src.Score import Score


# -----------------------------------------------------------------------------
# Sandu (Clifford Brown, 1955)
# -----------------------------------------------------------------------------
#
# 12-bar blues in Eb. Standard dominant blues form with ii-V turnarounds:
#
#   Bars 1-4:   Eb7   | Ab7   | Eb7    | Eb7
#   Bars 5-8:   Ab7   | Ab7   | Eb7    | Gm7 C7
#   Bars 9-12:  Fm7   | Bb7   | Eb7 C7 | Fm7 Bb7
#
# Bridge at bar 8-12 outlines a ii-V chain: Gm7-C7 → Fm7-Bb7 → Eb,
# then a turnaround Eb-C7-Fm7-Bb7 to set up the repeat.

SANDU = Score.from_bars(
    [
        # Bars 1-4
        "Eb7",      "Ab7",      "Eb7",      "Eb7",
        # Bars 5-8
        "Ab7",      "Ab7",      "Eb7",      "Gm7 C7",
        # Bars 9-12 (ii-V to turnaround)
        "Fm7",      "Bb7",      "Eb7 C7",   "Fm7 Bb7",
    ],
    title="Sandu",
    composer="Clifford Brown",
    tempo=140,
)


# -----------------------------------------------------------------------------
# Blue Bossa (Kenny Dorham, 1963)
# -----------------------------------------------------------------------------
#
# 16-bar AABA bossa nova in C minor with brief modulation to Db major.
# Compact form makes it ideal for practice and demo. Famous opening for
# beginner jazz students learning minor ii-V patterns.
#
#   A section (bars 1-8):
#     Cm7      | Cm7      | Fm7      | Fm7
#     Dm7b5    | G7       | Cm7      | Cm7
#
#   B section (bars 9-12) — modulation to Db major:
#     Ebm7     | Ab7      | Dbmaj7   | Dbmaj7
#
#   A return (bars 13-16) — back to Cm:
#     Dm7b5    | G7       | Cm7      | Cm7
#
# Note: "m7b5" is half-diminished 7 (same as "hdim7" or "ø7" in classical).

BLUE_BOSSA = Score.from_bars(
    [
        # A section
        "Cm7",      "Cm7",      "Fm7",      "Fm7",
        "Dm7b5",    "G7",       "Cm7",      "Cm7",
        # B section (modulation to Db)
        "Ebm7",     "Ab7",      "Dbmaj7",   "Dbmaj7",
        # A return
        "Dm7b5",    "G7",       "Cm7",      "Cm7",
    ],
    title="Blue Bossa",
    composer="Kenny Dorham",
    tempo=150,
)


# -----------------------------------------------------------------------------
# Registry — for selecting via CLI or programmatic access
# -----------------------------------------------------------------------------

ALL_SCORES = {
    "sandu":       SANDU,
    "blue_bossa":  BLUE_BOSSA,
}


def get_score(name: str) -> Score:
    """
    Look up a score by lowercase name.

    Raises ValueError if name is unknown.
    """
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in ALL_SCORES:
        available = sorted(ALL_SCORES.keys())
        raise ValueError(f"unknown score '{name}'. Available: {available}")
    return ALL_SCORES[key]