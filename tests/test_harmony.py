"""
Unit tests for harmony.analyze.

Covers:
  - Triad recognition (root position + inversions)
  - Seventh chord recognition
  - Multi-candidate ambiguity (dim7, power chords, shell voicings)
  - Subset matching (incomplete chords, shell voicings)
  - Foreign tone rejection
  - Key prior: diatonic boost and Roman numeral assignment
  - Edge cases: empty, single note, non-chord clusters
"""

import pytest
from whatthechord.note import Note
from whatthechord.scale import Scale
from whatthechord.chord import Chord
from whatthechord import harmony


# -----------------------------------------------------------------------------
# Basic triad recognition
# -----------------------------------------------------------------------------

def test_c_major_triad():
    chord = Chord([Note(60), Note(64), Note(67)])  # C-E-G
    results = harmony.analyze(chord)
    assert len(results) > 0
    top = results[0]
    assert top.root == 0
    assert top.quality == "maj"
    assert top.inversion == 0
    assert top.confidence == 1.0


def test_a_minor_triad():
    chord = Chord([Note(57), Note(60), Note(64)])  # A-C-E
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 9
    assert top.quality == "min"
    assert top.inversion == 0


def test_diminished_triad():
    chord = Chord([Note(59), Note(62), Note(65)])  # B-D-F
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 11
    assert top.quality == "dim"


def test_augmented_triad():
    chord = Chord([Note(60), Note(64), Note(68)])  # C-E-G#
    results = harmony.analyze(chord)
    top_aug = next(c for c in results if c.quality == "aug")
    assert top_aug.root == 0


# -----------------------------------------------------------------------------
# Inversions
# -----------------------------------------------------------------------------

def test_first_inversion():
    chord = Chord([Note(64), Note(67), Note(72)])  # E-G-C → C/E
    results = harmony.analyze(chord)
    c_maj = next(c for c in results if c.root == 0 and c.quality == "maj")
    assert c_maj.inversion == 1


def test_second_inversion():
    chord = Chord([Note(67), Note(72), Note(76)])  # G-C-E → C/G
    results = harmony.analyze(chord)
    c_maj = next(c for c in results if c.root == 0 and c.quality == "maj")
    assert c_maj.inversion == 2


# -----------------------------------------------------------------------------
# Seventh chords
# -----------------------------------------------------------------------------

def test_major_seventh():
    chord = Chord([Note(60), Note(64), Note(67), Note(71)])  # C-E-G-B
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 0
    assert top.quality == "maj7"
    assert top.confidence == 1.0


def test_dominant_seventh():
    chord = Chord([Note(60), Note(64), Note(67), Note(70)])  # C-E-G-Bb
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 0
    assert top.quality == "7"


def test_minor_seventh():
    chord = Chord([Note(60), Note(63), Note(67), Note(70)])  # C-Eb-G-Bb
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 0
    assert top.quality == "min7"


def test_half_diminished_seventh():
    chord = Chord([Note(60), Note(63), Note(66), Note(70)])  # C-Eb-Gb-Bb
    results = harmony.analyze(chord)
    top = results[0]
    assert top.root == 0
    assert top.quality == "m7b5"


def test_third_inversion_seventh():
    """7th in the bass = 3rd inversion."""
    chord = Chord([Note(58), Note(60), Note(64), Note(67)])  # Bb-C-E-G → C7/Bb
    results = harmony.analyze(chord)
    c_dom7 = next(c for c in results if c.root == 0 and c.quality == "7")
    assert c_dom7.inversion == 3


# -----------------------------------------------------------------------------
# Diminished 7th ambiguity
# -----------------------------------------------------------------------------

def test_diminished_seventh_four_rotations():
    """dim7 is symmetric: 4 enharmonic interpretations, all equally valid."""
    chord = Chord([Note(60), Note(63), Note(66), Note(69)])  # C-Eb-Gb-A
    results = harmony.analyze(chord)
    dim7s = [c for c in results if c.quality == "dim7"]
    assert len(dim7s) == 4
    # All four rotations have the same confidence
    confidences = {c.confidence for c in dim7s}
    assert len(confidences) == 1


# -----------------------------------------------------------------------------
# Subset matching (incomplete chords)
# -----------------------------------------------------------------------------

def test_shell_voicing_root_and_third():
    """Root + 3rd: identifies as major (with reduced confidence)."""
    chord = Chord([Note(60), Note(64)])  # C-E
    results = harmony.analyze(chord)
    c_maj = next(c for c in results if c.root == 0 and c.quality == "maj")
    # Weighted: root(1.0) + 3rd(1.75) out of 1.0+1.75+1.0 = 3.5
    expected = (1.0 + 1.75) / 3.75
    assert abs(c_maj.confidence - expected) < 0.01


def test_power_chord_ambiguous():
    """Root + 5th matches both major and minor templates."""
    chord = Chord([Note(60), Note(67)])  # C-G
    results = harmony.analyze(chord)
    c_maj = next((c for c in results if c.root == 0 and c.quality == "maj"), None)
    c_min = next((c for c in results if c.root == 0 and c.quality == "min"), None)
    assert c_maj is not None
    assert c_min is not None
    # Both should have same confidence (no 3rd to differentiate)
    assert abs(c_maj.confidence - c_min.confidence) < 0.01


def test_shell_voicing_third_and_seventh():
    """3rd + 7th: jazz shell voicing. High confidence due to weighting."""
    chord = Chord([Note(64), Note(70)])  # E-Bb → C7's 3rd + 7th
    results = harmony.analyze(chord)
    c_dom7 = next((c for c in results if c.root == 0 and c.quality == "7"), None)
    assert c_dom7 is not None
    # Weighted: 3rd(1.75) + 7th(1.75) out of 1.0+1.75+1.0+1.75 = 5.0
    expected = (1.75 + 1.75) / 5.50
    assert abs(c_dom7.confidence - expected) < 0.01


def test_shell_voicing_better_than_power_chord():
    """3rd+7th should score higher than root+5th (guide tones weighting)."""
    shell = Chord([Note(64), Note(70)])      # E-Bb (3rd+7th of C7)
    power = Chord([Note(60), Note(67)])      # C-G  (root+5th)

    shell_results = harmony.analyze(shell)
    power_results = harmony.analyze(power)

    # Best C7 interpretation
    shell_c7 = max(
        (c for c in shell_results if c.root == 0 and c.quality == "7"),
        key=lambda c: c.confidence,
    )
    # Best C major interpretation
    power_cmaj = max(
        (c for c in power_results if c.root == 0 and c.quality == "maj"),
        key=lambda c: c.confidence,
    )
    assert shell_c7.confidence > power_cmaj.confidence


# -----------------------------------------------------------------------------
# Foreign tone rejection
# -----------------------------------------------------------------------------

def test_chromatic_cluster_rejected():
    """C, C#, D — no template match, should return empty."""
    chord = Chord([Note(60), Note(61), Note(62)])
    results = harmony.analyze(chord)
    assert results == []


def test_c_major_with_added_fsharp_rejected():
    """C-E-G-F# has F# outside the major template, no match."""
    chord = Chord([Note(60), Note(64), Note(66), Note(67)])
    results = harmony.analyze(chord)
    # No quality template contains both 0,4,6,7 as exact subset
    c_results = [c for c in results if c.root == 0]
    assert c_results == []


# -----------------------------------------------------------------------------
# Edge cases
# -----------------------------------------------------------------------------

def test_empty_chord_returns_empty():
    chord = Chord([])
    results = harmony.analyze(chord)
    assert results == []


def test_single_note_returns_empty():
    chord = Chord([Note(60)])
    results = harmony.analyze(chord)
    assert results == []


def test_analyses_stored_on_chord():
    chord = Chord([Note(60), Note(64), Note(67)])
    harmony.analyze(chord)
    assert len(chord.analyses) > 0
    assert chord.analyses[0].quality == "maj"


# -----------------------------------------------------------------------------
# Key prior
# -----------------------------------------------------------------------------

def test_key_prior_assigns_roman_numeral():
    chord = Chord([Note(60), Note(64), Note(67)])  # C major
    c_major_scale = Scale.from_name("C", "major")
    results = harmony.analyze(chord, scale=c_major_scale)
    top = results[0]
    assert top.function == "I"


def test_key_prior_boosts_diatonic_confidence():
    """Diatonic chord (incomplete, so not already at 1.0) receives boost."""
    # Power chord: C-G. Multiple interpretations (Cmaj, Cmin, etc.) at 0.57.
    # In C major key, Cmaj (=I) should be boosted above Cmin (non-diatonic).
    chord = Chord([Note(60), Note(67)])
    c_major_scale = Scale.from_name("C", "major")

    without = harmony.analyze(chord)
    with_key = harmony.analyze(chord, scale=c_major_scale)

    c_maj_without = next(c for c in without if c.root == 0 and c.quality == "maj")
    c_maj_with = next(c for c in with_key if c.root == 0 and c.quality == "maj")
    assert c_maj_with.confidence > c_maj_without.confidence
    assert c_maj_with.function == "I"


def test_key_prior_v_chord():
    chord = Chord([Note(67), Note(71), Note(74)])  # G-B-D
    c_major_scale = Scale.from_name("C", "major")
    results = harmony.analyze(chord, scale=c_major_scale)
    top = results[0]
    assert top.root == 7
    assert top.quality == "maj"
    assert top.function == "V"


def test_key_prior_minor_chord_in_major_key():
    """ii chord in C major: D-F-A."""
    chord = Chord([Note(62), Note(65), Note(69)])  # D-F-A
    c_major_scale = Scale.from_name("C", "major")
    results = harmony.analyze(chord, scale=c_major_scale)
    top = results[0]
    assert top.root == 2
    assert top.quality == "min"
    assert top.function == "ii"


def test_key_prior_does_not_boost_nondiatonic():
    """Eb major triad in C major: root is non-diatonic, no boost."""
    chord = Chord([Note(63), Note(67), Note(70)])  # Eb-G-Bb
    c_major_scale = Scale.from_name("C", "major")
    results = harmony.analyze(chord, scale=c_major_scale)
    eb_maj = next(c for c in results if c.root == 3 and c.quality == "maj")
    # function should remain None (not in C major)
    assert eb_maj.function is None


def test_key_prior_in_minor_key():
    chord = Chord([Note(57), Note(60), Note(64)])  # A-C-E
    a_minor_scale = Scale.from_name("A", "minor")
    results = harmony.analyze(chord, scale=a_minor_scale)
    top = results[0]
    assert top.function == "i"


# -----------------------------------------------------------------------------
# Sort order
# -----------------------------------------------------------------------------

def test_results_sorted_by_confidence_descending():
    chord = Chord([Note(60), Note(64), Note(67), Note(70)])  # C7
    results = harmony.analyze(chord)
    confidences = [c.confidence for c in results]
    assert confidences == sorted(confidences, reverse=True)
