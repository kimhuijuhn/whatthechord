import Note

MODES = {
    "ionian": [(0, 'maj'), (2, 'min'), (4, 'min'), (5, 'maj'), (7, 'maj'), 
               (9, 'min'), (11, 'dim')],
}

class Scale:
    """
    Represents a musical scale. Defaults to major(ionian) scale.
    Does not contain octave information.

    Args:
        root(str): the pitch of a root note. 
        mode(str): the mode of a scale. (Default: "ionian")

    Attributes: 
        root(str): the pitch of a root note. 
        mode(str): the mode of a Scale. 
        notes(list): list of tuples containing (pitch, character) 
    """
    def __init__(self, root: str, mode='ionian'):
        self.root = root
        self.mode = mode
        
        # build list of  based on root pitch
        self.notes = []
        for m in MODES[self.mode]:
            self.notes.append((
                Note.NOTE_MAP[(Note.NOTE_MAP.index(root) + m[0]) % 12], m[1]))