"""
Unit tests for MidiInputHandler.

Tests handlers directly rather than through __call__ where possible —
this lets us avoid constructing raw MIDI byte sequences for every test.
The __call__ flow itself is exercised in dispatch tests.
"""

import pytest

from src.events import EventBuffer
from src.controller import MidiInputHandler
from src.midi_constants import MidiStatus


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def buf():
    return EventBuffer()


@pytest.fixture
def handler(buf):
    return MidiInputHandler(buf)


def make_event(message):
    """Mimic rtmidi callback signature: (message_bytes, delta_time)."""
    return (message, 0.0)


# -----------------------------------------------------------------------------
# Direct handler tests
# -----------------------------------------------------------------------------

def test_note_on_handler_adds_note(handler, buf):
    handler._handle_note_on([0x90, 60, 80])
    active = buf.get_active_notes()
    assert len(active) == 1
    assert active[0].value == 60
    assert active[0].velocity == 80


def test_note_off_handler_closes_note(handler, buf):
    handler._handle_note_on([0x90, 60, 80])
    handler._handle_note_off([0x80, 60, 0])
    assert buf.get_active_notes() == []
    assert len(buf) == 1


def test_note_on_with_velocity_zero_is_note_off(handler, buf):
    """MIDI convention: note-on with velocity 0 == note-off."""
    handler._handle_note_on([0x90, 60, 80])
    handler._handle_note_on([0x90, 60, 0])  # zero velocity = off
    assert buf.get_active_notes() == []


def test_short_note_on_message_ignored(handler, buf):
    """Note-on needs 3 bytes; shorter is malformed."""
    handler._handle_note_on([0x90, 60])  # missing velocity
    assert len(buf) == 0


def test_short_note_off_message_ignored(handler, buf):
    handler._handle_note_off([0x80])
    assert len(buf) == 0


# -----------------------------------------------------------------------------
# Dispatch via __call__
# -----------------------------------------------------------------------------

def test_call_dispatches_note_on(handler, buf):
    handler(make_event([0x90, 60, 100]))
    assert len(buf.get_active_notes()) == 1


def test_call_dispatches_note_off(handler, buf):
    handler(make_event([0x90, 60, 100]))
    handler(make_event([0x80, 60, 0]))
    assert buf.get_active_notes() == []


def test_call_with_channel_bits_still_dispatches():
    """Channel info is in the low nibble — STATUS_MASK strips it."""
    buf = EventBuffer()
    handler = MidiInputHandler(buf)
    handler(make_event([0x95, 60, 80]))  # NOTE_ON on channel 5
    assert len(buf.get_active_notes()) == 1


def test_call_ignores_unknown_status(handler, buf):
    """System exclusive (0xF0) is not in dispatch table — silently ignored."""
    handler(make_event([0xF0, 0x7F, 0x00]))
    assert len(buf) == 0


def test_call_ignores_program_change(handler, buf):
    """Program Change (0xC0) is 2-byte — not registered in dispatch."""
    handler(make_event([0xC0, 5]))
    assert len(buf) == 0


def test_call_ignores_short_message(handler, buf):
    """1-byte system real-time messages (clock, active sensing, etc.)."""
    handler(make_event([0xF8]))  # MIDI clock
    assert len(buf) == 0


def test_call_with_empty_message_does_not_crash(handler, buf):
    handler(make_event([]))
    assert len(buf) == 0


# -----------------------------------------------------------------------------
# Control Change & Pitch Bend (currently stubs, but shouldn't crash)
# -----------------------------------------------------------------------------

def test_cc_message_does_not_crash(handler, buf):
    """Sustain pedal CC — handler is a stub for now, just ensure no error."""
    handler(make_event([0xB0, 64, 127]))  # sustain on
    handler(make_event([0xB0, 64, 0]))    # sustain off
    # No notes added, but no exception either
    assert len(buf) == 0


def test_short_cc_message_ignored(handler, buf):
    handler._handle_cc([0xB0, 64])  # missing value
    # Should not crash


def test_pitch_bend_does_not_crash(handler, buf):
    handler(make_event([0xE0, 0x00, 0x40]))  # center
    assert len(buf) == 0


def test_short_pitch_bend_ignored(handler, buf):
    handler._handle_pitch_bend([0xE0, 0x00])
    # Should not crash


# -----------------------------------------------------------------------------
# Sequences (integration-ish)
# -----------------------------------------------------------------------------

def test_chord_sequence_through_dispatcher(handler, buf):
    """Press C major, then release each note in order."""
    handler(make_event([0x90, 60, 80]))
    handler(make_event([0x90, 64, 80]))
    handler(make_event([0x90, 67, 80]))
    assert len(buf.get_active_notes()) == 3

    handler(make_event([0x80, 60, 0]))
    assert {n.value for n in buf.get_active_notes()} == {64, 67}

    handler(make_event([0x80, 64, 0]))
    handler(make_event([0x80, 67, 0]))
    assert buf.get_active_notes() == []
    assert len(buf) == 3


def test_retrigger_through_dispatcher(handler, buf):
    handler(make_event([0x90, 60, 80]))
    handler(make_event([0x90, 60, 100]))  # retrigger
    handler(make_event([0x80, 60, 0]))

    assert buf.get_active_notes() == []
    assert len(buf) == 2