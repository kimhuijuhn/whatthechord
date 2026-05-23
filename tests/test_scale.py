"""
Unit tests for ScaleType and Scale.

Covers:
  - ScaleType Enum: intervals, alias behavior (MAJOR == IONIAN, MINOR == AEOLIAN)
  - Scale construction: direct, from_name, from_midi_key_signature
  - Validation: invalid tonic, mode, MIDI ranges
  - Diatonic queries: is_diatonic, degree_of, pitch_classes
  - Diatonic triads: pitches, quality, roman numerals
  - Frozen / hashable / immutable
"""

import pytest
from whatthechord.scale import Scale 
from whatthechord.scale_type import ScaleType

# =============================================================================
# ScaleType (Enum)
# =============================================================================

def test_major_intervals():
    assert ScaleType.MAJOR.intervals == (0, 2, 4, 5, 7, 9, 11)
    assert ScaleType.MAJOR.num_degrees == 7


def test_minor_intervals():
    """Natural minor."""
    assert ScaleType.MINOR.intervals == (0, 2, 3, 5, 7, 8, 10)
    assert ScaleType.MINOR.num_degrees == 7


def test_ionian_is_alias_of_major():
    """Same value → automatic alias in Python Enum."""
    assert ScaleType.IONIAN is ScaleType.MAJOR
    assert ScaleType.IONIAN.name == "MAJOR"  # canonical name


def test_aeolian_is_alias_of_minor():
    assert ScaleType.AEOLIAN is ScaleType.MINOR
    assert ScaleType.AEOLIAN.name == "MINOR"


def test_iteration_excludes_aliases():
    """For loop sees canonical members only."""
    names = [st.name for st in ScaleType]
    assert names == ["MAJOR", "MINOR", "DORIAN", "PHRYGIAN", "LYDIAN", 
                     "MIXOLYDIAN", "LOCRIAN", "HARMONIC_MINOR", 
                     "MELODIC_MINOR"]


def test_members_includes_aliases():
    """__members__ dict includes aliases for lookup."""
    assert "IONIAN" in ScaleType.__members__
    assert "AEOLIAN" in ScaleType.__members__
    assert ScaleType.__members__["IONIAN"] is ScaleType.MAJOR


# =============================================================================
# Scale construction
# =============================================================================

def test_direct_construction():
    s = Scale(tonic=0, scale_type=ScaleType.MAJOR)
    assert s.tonic == 0
    assert s.scale_type is ScaleType.MAJOR
    assert s.mode == "major"
    assert s.tonic_name == "C"


def test_invalid_tonic_raises():
    with pytest.raises(ValueError):
        Scale(tonic=12, scale_type=ScaleType.MAJOR)
    with pytest.raises(ValueError):
        Scale(tonic=-1, scale_type=ScaleType.MAJOR)


# =============================================================================
# from_name
# =============================================================================

def test_from_name_default_major():
    s = Scale.from_name("C")
    assert s.tonic == 0
    assert s.mode == "major"


def test_from_name_explicit_major():
    s = Scale.from_name("G", "major")
    assert s.tonic == 7
    assert s.mode == "major"


def test_from_name_minor():
    s = Scale.from_name("A", "minor")
    assert s.tonic == 9
    assert s.mode == "minor"


def test_from_name_ionian_alias():
    """User input 'ionian' should resolve to MAJOR."""
    s = Scale.from_name("C", "ionian")
    assert s.scale_type is ScaleType.MAJOR
    assert s.mode == "major"


def test_from_name_aeolian_alias():
    s = Scale.from_name("A", "aeolian")
    assert s.scale_type is ScaleType.MINOR
    assert s.mode == "minor"


def test_from_name_case_insensitive():
    s1 = Scale.from_name("C", "MAJOR")
    s2 = Scale.from_name("C", "major")
    s3 = Scale.from_name("C", "Major")
    assert s1 == s2 == s3


def test_from_name_sharp_normalized():
    """Bb is normalized to A# via ENHARMONIC_SHARP."""
    s = Scale.from_name("A#", "major")
    assert s.tonic == 10
    assert s.tonic_name == "Bb"


def test_from_name_unknown_tonic_raises():
    with pytest.raises(ValueError):
        Scale.from_name("X", "major")


def test_from_name_unknown_mode_raises():
    with pytest.raises(ValueError):
        Scale.from_name("C", "SUPER_LOCRIAN")  # not yet registered


# =============================================================================
# from_midi_key_signature
# =============================================================================

def test_midi_c_major():
    s = Scale.from_midi_key_signature(0, 0)
    assert s.tonic == 0
    assert s.mode == "major"


def test_midi_g_major():
    """1 sharp = G major."""
    s = Scale.from_midi_key_signature(1, 0)
    assert s.tonic == 7


def test_midi_d_minor():
    """1 flat, minor → D minor (relative of F major)."""
    s = Scale.from_midi_key_signature(-1, 1)
    assert s.tonic == 2
    assert s.mode == "minor"


def test_midi_a_minor():
    """0 sharps/flats, minor → A minor (relative of C major)."""
    s = Scale.from_midi_key_signature(0, 1)
    assert s.tonic == 9


def test_midi_out_of_range():
    with pytest.raises(ValueError):
        Scale.from_midi_key_signature(8, 0)
    with pytest.raises(ValueError):
        Scale.from_midi_key_signature(-8, 0)


# =============================================================================
# Diatonic queries — C major
# =============================================================================

def test_c_major_pitch_classes():
    s = Scale.from_name("C", "major")
    assert s.pitch_classes == {0, 2, 4, 5, 7, 9, 11}


def test_c_major_is_diatonic():
    s = Scale.from_name("C", "major")
    assert s.is_diatonic(0)   # C
    assert s.is_diatonic(4)   # E
    assert not s.is_diatonic(1)   # C#
    assert not s.is_diatonic(6)   # F#


def test_c_major_degree_of():
    s = Scale.from_name("C", "major")
    assert s.degree_of(0) == 1   # C → 1
    assert s.degree_of(4) == 3   # E → 3
    assert s.degree_of(7) == 5   # G → 5
    assert s.degree_of(11) == 7  # B → 7
    assert s.degree_of(1) is None  # C# non-diatonic


# =============================================================================
# Diatonic queries — A minor
# =============================================================================

def test_a_minor_pitch_classes():
    """A natural minor shares pitch classes with C major."""
    s = Scale.from_name("A", "minor")
    assert s.pitch_classes == {9, 11, 0, 2, 4, 5, 7}


def test_a_minor_degree_of():
    s = Scale.from_name("A", "minor")
    assert s.degree_of(9) == 1
    assert s.degree_of(0) == 3
    assert s.degree_of(4) == 5


# =============================================================================
# Diatonic triads — C major
# =============================================================================

def test_c_major_I():
    s = Scale.from_name("C", "major")
    assert s.diatonic_triad_pitches(1) == (0, 4, 7)  # C-E-G
    assert s.diatonic_triad_quality(1) == "maj"
    assert s.roman_numeral(1) == "I"


def test_c_major_ii():
    s = Scale.from_name("C", "major")
    assert s.diatonic_triad_pitches(2) == (2, 5, 9)  # D-F-A
    assert s.diatonic_triad_quality(2) == "min"
    assert s.roman_numeral(2) == "ii"


def test_c_major_V():
    """V triad wraps around the scale (D is below the root G)."""
    s = Scale.from_name("C", "major")
    assert s.diatonic_triad_pitches(5) == (7, 11, 2)  # G-B-D
    assert s.diatonic_triad_quality(5) == "maj"
    assert s.roman_numeral(5) == "V"


def test_c_major_vii_dim():
    s = Scale.from_name("C", "major")
    assert s.diatonic_triad_pitches(7) == (11, 2, 5)  # B-D-F
    assert s.diatonic_triad_quality(7) == "dim"
    assert s.roman_numeral(7) == "vii°"


# =============================================================================
# Diatonic triads — A minor
# =============================================================================

def test_a_minor_i():
    s = Scale.from_name("A", "minor")
    assert s.diatonic_triad_pitches(1) == (9, 0, 4)  # A-C-E
    assert s.diatonic_triad_quality(1) == "min"
    assert s.roman_numeral(1) == "i"


def test_a_minor_iv():
    """Natural minor iv is minor (not major as in harmonic minor)."""
    s = Scale.from_name("A", "minor")
    assert s.diatonic_triad_pitches(4) == (2, 5, 9)  # D-F-A
    assert s.diatonic_triad_quality(4) == "min"
    assert s.roman_numeral(4) == "iv"


def test_a_minor_VII():
    """Natural minor VII is major (subtonic, not leading tone)."""
    s = Scale.from_name("A", "minor")
    assert s.diatonic_triad_pitches(7) == (7, 11, 2)  # G-B-D
    assert s.diatonic_triad_quality(7) == "maj"
    assert s.roman_numeral(7) == "VII"


def test_invalid_degree():
    s = Scale.from_name("C", "major")
    with pytest.raises(ValueError):
        s.diatonic_triad_pitches(0)
    with pytest.raises(ValueError):
        s.diatonic_triad_pitches(8)
    with pytest.raises(ValueError):
        s.roman_numeral(0)
    with pytest.raises(ValueError):
        s.roman_numeral(8)


# =============================================================================
# Frozen / hashable / equality
# =============================================================================

def test_scale_is_hashable():
    """Frozen dataclass can be used as dict key."""
    s1 = Scale.from_name("C", "major")
    s2 = Scale.from_name("C", "major")
    cache = {s1: "result"}
    assert cache[s2] == "result"


def test_scale_is_immutable():
    s = Scale.from_name("C", "major")
    with pytest.raises(Exception):  # FrozenInstanceError
        s.tonic = 5


def test_scale_equality():
    s1 = Scale.from_name("C", "major")
    s2 = Scale(tonic=0, scale_type=ScaleType.MAJOR)
    assert s1 == s2
    # Alias should resolve to the same scale_type
    s3 = Scale(tonic=0, scale_type=ScaleType.IONIAN)
    assert s1 == s3


def test_scale_inequality():
    c_major = Scale.from_name("C", "major")
    a_minor = Scale.from_name("A", "minor")
    g_major = Scale.from_name("G", "major")
    assert c_major != a_minor
    assert c_major != g_major


def test_scale_repr():
    s = Scale.from_name("C", "major")
    assert "C" in repr(s)
    assert "major" in repr(s)