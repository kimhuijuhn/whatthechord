"""
Unit tests for Chord container.

Verifies:
  - Empty / single-note / multi-note construction
  - Deduplication by MIDI value
  - Octave handling (doubled notes, bass)
  - Sort order (low to high)
  - Properties: pitch_classes, bass, is_empty, is_analyzable
  - Constructor methods preserve all the above
  - is_analyzable accepts power chords and shell voicings (2-note)
"""

import pytest
from whatthechord.note import Note
from whatthechord.chord import Chord


# -----------------------------------------------------------------------------
# Construction
# -----------------------------------------------------------------------------

def test_empty_chord():
    chord = Chord([])
    assert chord.is_empty
    assert not chord.is_analyzable
    assert len(chord) == 0
    assert chord.bass is None
    assert chord.pitch_classes == set()


def test_single_note_not_analyzable():
    chord = Chord([Note(60)])  # C4
    assert not chord.is_empty
    assert not chord.is_analyzable  # need at least 2 pitch classes
    assert len(chord) == 1
    assert chord.bass.value == 60


def test_two_notes_is_analyzable():
    """Power chord — root + 5th, minimal analyzable voicing."""
    chord = Chord([Note(60), Note(67)])  # C + G
    assert chord.is_analyzable
    assert len(chord) == 2


def test_shell_voicing_is_analyzable():
    """Jazz shell voicing — 3rd + 7th only, common comping pattern."""
    chord = Chord([Note(64), Note(70)])  # E + Bb (3rd + 7th of C7)
    assert chord.is_analyzable


def test_triad_is_analyzable():
    chord = Chord([Note(60), Note(64), Note(67)])  # C major
    assert chord.is_analyzable
    assert chord.pitch_classes == {0, 4, 7}


def test_seventh_chord_is_analyzable():
    chord = Chord([Note(60), Note(64), Note(67), Note(71)])  # Cmaj7
    assert chord.is_analyzable
    assert len(chord) == 4
    assert chord.pitch_classes == {0, 4, 7, 11}


# -----------------------------------------------------------------------------
# Deduplication and ordering
# -----------------------------------------------------------------------------

def test_deduplicate_exact_midi_values():
    """Same MIDI value twice should appear once."""
    chord = Chord([Note(60), Note(60), Note(64)])
    assert len(chord) == 2
    values = [n.value for n in chord.notes]
    assert values == [60, 64]


def test_doubled_octaves_kept_separate():
    """C2 + C4 are both 'C' — kept as separate notes (different MIDI values)."""
    chord = Chord([Note(36), Note(60)])  # C2, C4
    assert len(chord) == 2
    # But pitch_classes collapses them
    assert chord.pitch_classes == {0}
    # And is_analyzable should be False — only 1 distinct pitch class
    assert not chord.is_analyzable


def test_notes_sorted_low_to_high():
    chord = Chord([Note(67), Note(60), Note(64)])  # input out of order
    values = [n.value for n in chord.notes]
    assert values == [60, 64, 67]


def test_bass_is_lowest_note():
    chord = Chord([Note(67), Note(60), Note(64)])
    assert chord.bass.value == 60


def test_bass_with_doubled_root():
    """C2 + C4 + E4 + G4 — bass is C2 (lowest)."""
    chord = Chord([Note(36), Note(60), Note(64), Note(67)])
    assert chord.bass.value == 36
    assert chord.is_analyzable
    assert chord.pitch_classes == {0, 4, 7}


def test_first_inversion_bass_is_third():
    """C/E voicing: E in bass, C and G above."""
    chord = Chord([Note(64), Note(72), Note(79)])  # E4, C5, G5
    assert chord.bass.value == 64
    assert chord.pitch_classes == {0, 4, 7}


# -----------------------------------------------------------------------------
# pitch_classes
# -----------------------------------------------------------------------------

def test_pitch_classes_octave_independent():
    """C2, E4, G6 should all collapse to {0, 4, 7}."""
    chord = Chord([Note(36), Note(64), Note(91)])
    assert chord.pitch_classes == {0, 4, 7}


def test_pitch_classes_chromatic_cluster():
    """3 distinct pitch classes — is_analyzable passes the cheap filter,
    but harmony.analyze will return no matches (not a real chord)."""
    chord = Chord([Note(60), Note(61), Note(62)])  # C, C#, D
    assert chord.pitch_classes == {0, 1, 2}
    assert chord.is_analyzable


# -----------------------------------------------------------------------------
# Constructors
# -----------------------------------------------------------------------------

def test_from_active_notes():
    notes = [Note(60), Note(64), Note(67)]
    chord = Chord.from_active_notes(notes)
    assert chord.is_analyzable
    assert chord.pitch_classes == {0, 4, 7}


def test_from_recent_notes():
    notes = [Note(60), Note(64), Note(67)]
    chord = Chord.from_recent_notes(notes)
    assert chord.is_analyzable


def test_constructor_does_not_share_input_list():
    """Mutating the original notes list after construction must not affect chord."""
    notes = [Note(60), Note(64), Note(67)]
    chord = Chord(notes)
    notes.append(Note(70))  # mutate original
    assert len(chord) == 3  # unaffected


# -----------------------------------------------------------------------------
# repr / len (smoke tests)
# -----------------------------------------------------------------------------

def test_len_matches_notes_count():
    chord = Chord([Note(60), Note(64), Note(67)])
    assert len(chord) == 3


def test_repr_unanalyzed():
    chord = Chord([Note(60), Note(64), Note(67)])
    r = repr(chord)
    assert "C4" in r and "E4" in r and "G4" in r


def test_repr_empty():
    """Should not crash on empty chord."""
    chord = Chord([])
    repr(chord)  # just confirm no exception
