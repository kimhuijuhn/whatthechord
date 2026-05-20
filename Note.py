NOTE_MAP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Note:
    """ 
    Represents a musical note.

    Attributes:
        value(int): MIDI value of a Note.
        pitch(str): pitch of a Note.
        octave(int): the octave value of a Note.
    """
    def __init__(self, val):
        """ Create a Note instance given a MIDI value. """
        self.value = val
        self.pitch = NOTE_MAP[val % 12]
        self.octave = (val // 12) - 1   

    def __str__(self):
        """ String representation of a Note instance (ex. C4) """
        return f"{self.pitch}{self.octave}"
    
    def __repr__(self):
        """ String representation of a Note instance (ex. C4) """
        return f"{self.pitch}{self.octave}"
    
    def __eq__(self, other):
        """ Two notes are equal when their octave and pitch is equal """
        if not isinstance(other, Note):
            return NotImplemented
        return self.pitch == other.pitch and self.octave == other.octave

    def get_interval(self, other):
        return abs(self.value - other.value) % 12
    
    def get_midi_value(self):
        return self.value
    
    # Utility methods

    def init_from_char(char, octave):
        # validate if char is a note
        if char not in NOTE_MAP:
            print("Invalid character.")
            return
        
        # build a Note with the requested pitch and octave
        midi_value = NOTE_MAP.index(char) + (12 * (octave + 1))

        return Note(midi_value)