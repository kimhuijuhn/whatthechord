"""
Note: a single MIDI note with timing and pitch information.

Note spellings default to flats (Eb, Bb, Ab, Db, Gb) — the convention
in jazz lead sheets (Real Book, iReal Pro). Sharp spelling is available
via `pitch_sharp` property for sharp-key contexts.
"""

from typing import Optional


# -----------------------------------------------------------------------------
# Pitch class name maps
# -----------------------------------------------------------------------------

# Default: flat-spelled note names. Standard in jazz.
NOTE_MAP = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Sharp-spelled note names. Reserved for sharp-key contexts (rare in jazz,
# but used in classical and some pop). Same pitch classes as NOTE_MAP.
NOTE_MAP_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Sharp → flat normalization. Used by parsers to accept either spelling
# while storing internally as flat (the default convention).
ENHARMONIC_FLAT = {
    "C#": "Db",
    "D#": "Eb",
    "F#": "Gb",
    "G#": "Ab",
    "A#": "Bb",
}

# Flat → sharp (output direction). For displaying notes in sharp-key
# contexts. Currently used rarely — most jazz lead sheets favor flats.
ENHARMONIC_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}


# -----------------------------------------------------------------------------
# Note
# -----------------------------------------------------------------------------

class Note:
    """
    Represents a musical note.

    Attributes:
        value (int): MIDI value of a Note (0-127).
        pitch (str): Flat-spelled pitch name (e.g., 'Eb', 'Bb'). Default.
        octave (int): The octave value of a Note (e.g., C4 = middle C).
        velocity (int): MIDI velocity (0-127).
        on_time (float | None): Timestamp when note-on received.
        off_time (float | None): Timestamp when note-off received.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def __init__(self, val: int, velocity: int = 64):
        """ Create a Note instance given a MIDI value. """
        self.value = val
        self.pitch = NOTE_MAP[val % 12]
        self.octave = (val // 12) - 1
        self.velocity = velocity
        self.on_time: Optional[float] = None
        self.off_time: Optional[float] = None

    @classmethod
    def from_pitch(cls, pitch: str, octave: int, velocity: int = 64):
        """
        Create a Note from a pitch name and octave.

        Accepts both flat and sharp spellings: from_pitch("Eb", 4) and
        from_pitch("D#", 4) produce the same Note.
        """
        # Normalize sharp input to flat (the canonical form)
        pitch = ENHARMONIC_FLAT.get(pitch, pitch)
        if pitch not in NOTE_MAP:
            raise ValueError(f"unknown pitch '{pitch}'")
        return cls((octave + 1) * 12 + NOTE_MAP.index(pitch), velocity)


    # -------------------------------------------------------------------------
    # Time-related Methods
    # -------------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """ True while sustaining (note-on received, note-off not yet). """
        return self.on_time is not None and self.off_time is None

    @property
    def duration(self) -> Optional[float]:
        """ Seconds between on_time and off_time. None if not yet completed. """
        if self.on_time is None or self.off_time is None:
            return None
        return self.off_time - self.on_time

    def set_on_time(self, timestamp: float) -> None:
        self.on_time = timestamp

    def set_off_time(self, timestamp: float) -> None:
        self.off_time = timestamp


    # -------------------------------------------------------------------------
    # Pitch-related Methods
    # -------------------------------------------------------------------------

    @property
    def pitch_sharp(self) -> str:
        """
        Sharp-spelled pitch name (e.g., 'D#' instead of 'Eb').

        Use in sharp-key contexts (B major, E major, etc.). Default
        `pitch` returns flat spelling, which is the jazz convention.
        """
        return NOTE_MAP_SHARP[self.value % 12]

    def get_interval(self, other: "Note") -> int:
        """Distance in semitones, modulo 12."""
        return abs(self.value - other.value) % 12

    def get_midi_value(self) -> int:
        return self.value

    def has_same_pitch(self, other: "Note") -> bool:
        """ Pitch + octave equality, ignoring timing. For chord analysis. """
        if not isinstance(other, Note):
            return NotImplemented
        return self.pitch == other.pitch and self.octave == other.octave


    # -------------------------------------------------------------------------
    # Special Methods
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """ String representation (e.g., 'Eb4'). """
        return f"{self.pitch}{self.octave}"

    def __repr__(self) -> str:
        if self.on_time is None:
            return f"Note({self.pitch}{self.octave})"
        state = "active" if self.is_active else f"{self.duration:.2f}s"
        return f"Note({self.pitch}{self.octave}, {state})"