NOTE_MAP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Enharmonically equivalents
ENHARMONIC_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}


class Note:
    """ 
    Represents a musical note.

    Attributes:
        value(int): MIDI value of a Note.
        pitch(str): pitch of a Note.
        octave(int): the octave value of a Note.
        on_time(float): Timestamp
    """


    # -------------------------------------------------------------------------
    # Lifecycle 
    # -------------------------------------------------------------------------

    def __init__(self, val, velocity: int = 64):
        """ Create a Note instance given a MIDI value. """
        self.value = val
        self.pitch = NOTE_MAP[val % 12]
        self.octave = (val // 12) - 1
        self.velocity = velocity
        self.on_time = None
        self.off_time = None

    @classmethod
    def from_pitch(cls, pitch, octave, velocity: int = 64):
        return cls((octave + 1) * 12 + NOTE_MAP.index(pitch), velocity)


    # -------------------------------------------------------------------------
    # Time-related Methods
    # -------------------------------------------------------------------------
    
    @property
    def is_active(self) -> bool:
        """ True while sustaining (note-on received, note-off not yet). """
        #TODO: implement active notes with off notes but with sustain pedal on
        return self.on_time is not None and self.off_time is None

    @property
    def duration(self) -> float | None:
        """ Seconds between on_time and off_time. None if not yet completed. """
        if self.on_time is None or self.off_time is None:
            return None
        return self.off_time - self.on_time
    
    def set_on_time(self, timestamp):
        self.on_time = timestamp
    
    def set_off_time(self, timestamp):
        self.off_time = timestamp


    # -------------------------------------------------------------------------
    # Pitch-related Methods
    # -------------------------------------------------------------------------

    def get_interval(self, other):
        return abs(self.value - other.value) % 12
    
    def get_midi_value(self):
        return self.value
    
    def has_same_pitch(self, other):
        """ Two notes are equal when their octave and pitch is equal """
        if not isinstance(other, Note):
            return NotImplemented
        return self.pitch == other.pitch and self.octave == other.octave

    # -------------------------------------------------------------------------
    # Special Methods
    # -------------------------------------------------------------------------
    
    def __str__(self):
        """ String representation of a Note instance (ex. C4) """
        return f"{self.pitch}{self.octave}"
    
    def __repr__(self) -> str:
        if self.on_time is None:
            return f"Note({self.pitch}{self.octave})"
        state = "active" if self.is_active else f"{self.duration:.2f}s"
        return f"Note({self.pitch}{self.octave}, {state})"
    
    