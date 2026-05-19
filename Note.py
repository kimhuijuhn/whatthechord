NOTE_MAP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Note:
    def __init__(self, val):
        """ Create a Note instance given a MIDI value. """
        self.pitch = NOTE_MAP[val % 12]
        self.octave = (val // 12) - 1   

    def __str__(self):
        return f"{self.pitch}{self.octave}"
    
    def __repr__(self):
        return f"{self.pitch}{self.octave}"
    
    def __eq__(self, other):
        if not isinstance(other, Note):
            return NotImplemented
        return self.pitch == other.pitch and self.octave == other.octave
