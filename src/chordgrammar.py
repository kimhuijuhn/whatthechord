from src.Note import Note
from src.Scale import Scale, MODES

def detect_primary_triad(note_list, key, mode='ionian'):
    # convert Notes to intervals 
    root = Note.init_from_char(key, 0)
    input_note_intervals = [Note.get_interval(n, root) for n in note_list]
