"""
Unit tests for EventBuffer.

Covers:
  - Basic on/off lifecycle
  - Multiple simultaneous notes (chord)
  - Retrigger (same pitch pressed before release)
  - Spurious note-off (off without prior on)
  - get_recent_notes window filtering
  - get_all_notes / get_active_notes snapshot independence
  - Thread safety under concurrent writes
  - __len__
"""

import threading
import time

from whatthechord.events import EventBuffer


# -----------------------------------------------------------------------------
# Basic lifecycle
# -----------------------------------------------------------------------------

def test_empty_buffer_has_no_notes():
    buf = EventBuffer()
    assert len(buf) == 0
    assert buf.get_active_notes() == []
    assert buf.get_all_notes() == []


def test_note_on_creates_active_note():
    buf = EventBuffer()
    buf.on_note_on(60, velocity=80)

    active = buf.get_active_notes()
    assert len(active) == 1
    assert active[0].value == 60
    assert active[0].velocity == 80
    assert active[0].is_active
    assert active[0].on_time is not None
    assert active[0].off_time is None


def test_note_off_closes_note():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_off(60)

    # No longer active
    assert buf.get_active_notes() == []
    # But still in full history
    all_notes = buf.get_all_notes()
    assert len(all_notes) == 1
    note = all_notes[0]
    assert not note.is_active
    assert note.off_time is not None
    assert note.duration is not None
    assert note.duration >= 0


def test_note_timestamps_are_monotonic():
    buf = EventBuffer()
    buf.on_note_on(60)
    time.sleep(0.01)
    buf.on_note_off(60)

    note = buf.get_all_notes()[0]
    assert note.on_time < note.off_time


# -----------------------------------------------------------------------------
# Multiple notes
# -----------------------------------------------------------------------------

def test_chord_three_simultaneous_notes():
    """C major triad held down."""
    buf = EventBuffer()
    buf.on_note_on(60)  # C
    buf.on_note_on(64)  # E
    buf.on_note_on(67)  # G

    active = buf.get_active_notes()
    assert len(active) == 3
    assert {n.value for n in active} == {60, 64, 67}
    assert all(n.is_active for n in active)


def test_release_one_of_three_notes():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_on(64)
    buf.on_note_on(67)
    buf.on_note_off(64)

    active = buf.get_active_notes()
    assert {n.value for n in active} == {60, 67}
    # Full history still has all three
    assert len(buf.get_all_notes()) == 3


# -----------------------------------------------------------------------------
# Retrigger
# -----------------------------------------------------------------------------

def test_retrigger_closes_previous_note():
    """Same pitch pressed twice without release in between."""
    buf = EventBuffer()
    buf.on_note_on(60, velocity=80)
    first = buf.get_all_notes()[0]
    time.sleep(0.01)

    buf.on_note_on(60, velocity=100)

    # Previous note is closed
    assert not first.is_active
    assert first.off_time is not None
    assert first.duration is not None

    # New note is active with new velocity
    active = buf.get_active_notes()
    assert len(active) == 1
    assert active[0] is not first  # different instance
    assert active[0].velocity == 100

    # History has both
    assert len(buf) == 2


def test_retrigger_then_off_only_closes_current():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_on(60)  # retrigger
    buf.on_note_off(60)

    assert buf.get_active_notes() == []
    all_notes = buf.get_all_notes()
    assert len(all_notes) == 2
    # Both should have off_time set
    assert all(not n.is_active for n in all_notes)


# -----------------------------------------------------------------------------
# Spurious off
# -----------------------------------------------------------------------------

def test_note_off_without_prior_on_is_silently_ignored():
    buf = EventBuffer()
    buf.on_note_off(60)  # never pressed

    assert len(buf) == 0
    assert buf.get_active_notes() == []
    assert buf.get_all_notes() == []


def test_note_off_twice_is_idempotent():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_off(60)
    buf.on_note_off(60)  # second off, no active note left

    assert len(buf) == 1
    assert buf.get_active_notes() == []


# -----------------------------------------------------------------------------
# get_recent_notes
# -----------------------------------------------------------------------------

def test_recent_notes_includes_active_notes_always():
    """An active (sustaining) note should always be in 'recent'."""
    buf = EventBuffer()
    buf.on_note_on(60)
    time.sleep(0.1)  # 100ms passes

    # Window of 50ms — but the note is still active, so include it
    recent = buf.get_recent_notes(window_sec=0.05)
    assert len(recent) == 1
    assert recent[0].value == 60


def test_recent_notes_excludes_old_closed_notes():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_off(60)
    time.sleep(0.1)

    recent = buf.get_recent_notes(window_sec=0.05)
    assert recent == []


def test_recent_notes_includes_recently_closed():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_off(60)
    # Don't sleep — just-closed note is still within window

    recent = buf.get_recent_notes(window_sec=1.0)
    assert len(recent) == 1
    assert recent[0].value == 60


def test_recent_notes_mixed():
    """Old closed + recent closed + active should give recent + active."""
    buf = EventBuffer()
    # Old: played and released early
    buf.on_note_on(48)
    buf.on_note_off(48)
    time.sleep(0.15)

    # Recent: played and released just now
    buf.on_note_on(60)
    buf.on_note_off(60)

    # Sustaining
    buf.on_note_on(72)

    recent = buf.get_recent_notes(window_sec=0.1)
    values = {n.value for n in recent}
    assert 48 not in values   # too old
    assert 60 in values       # recent closed
    assert 72 in values       # active


# -----------------------------------------------------------------------------
# Snapshot independence
# -----------------------------------------------------------------------------

def test_get_active_notes_returns_new_list():
    """Mutating returned list must not affect buffer."""
    buf = EventBuffer()
    buf.on_note_on(60)

    active = buf.get_active_notes()
    active.clear()  # mutate the returned list

    # Buffer is unaffected
    assert len(buf.get_active_notes()) == 1


def test_get_all_notes_returns_new_list():
    buf = EventBuffer()
    buf.on_note_on(60)
    buf.on_note_off(60)

    all_notes = buf.get_all_notes()
    all_notes.clear()

    assert len(buf.get_all_notes()) == 1


def test_returned_notes_share_instances():
    """
    Snapshot is shallow: the Note instances are the same objects.
    This is by design — buffer is single source of truth.
    """
    buf = EventBuffer()
    buf.on_note_on(60)

    active_first = buf.get_active_notes()
    active_second = buf.get_active_notes()
    assert active_first[0] is active_second[0]

    # And the same instance appears in full history
    assert buf.get_all_notes()[0] is active_first[0]


# -----------------------------------------------------------------------------
# Thread safety
# -----------------------------------------------------------------------------

def test_concurrent_writes_no_data_loss():
    """Many threads writing simultaneously — all events recorded."""
    buf = EventBuffer()

    def writer(pitch_start: int, count: int):
        for i in range(count):
            pitch = pitch_start + (i % 12)
            buf.on_note_on(pitch)
            buf.on_note_off(pitch)

    threads = [
        threading.Thread(target=writer, args=(40 + i * 12, 25))
        for i in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Each writer pushed 25 notes, 4 writers → 100 total
    assert len(buf) == 100
    assert buf.get_active_notes() == []


def test_concurrent_read_during_writes():
    """Reader should never crash even with concurrent writes."""
    buf = EventBuffer()
    stop_flag = threading.Event()
    errors = []

    def reader():
        try:
            while not stop_flag.is_set():
                _ = buf.get_active_notes()
                _ = buf.get_all_notes()
                _ = buf.get_recent_notes(0.5)
                _ = len(buf)
        except Exception as e:
            errors.append(e)

    def writer():
        for i in range(200):
            buf.on_note_on(60 + (i % 12))
            buf.on_note_off(60 + (i % 12))

    reader_thread = threading.Thread(target=reader)
    writer_thread = threading.Thread(target=writer)
    reader_thread.start()
    writer_thread.start()

    writer_thread.join()
    stop_flag.set()
    reader_thread.join(timeout=1.0)

    assert errors == [], f"Reader saw errors: {errors}"
    assert len(buf) == 200