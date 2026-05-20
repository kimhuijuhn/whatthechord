from Note import Note
from Scale import Scale

def detect_primary_triad(note_list, key, mode='ionian'):
    # convert Notes to intervals 
    root = Note.init_from_char(key, 0)
    interval_list = [Note.get_interval(n, root) for n in note_list]

    if 0 in interval_list and 4 in interval_list and 7 in interval_list:
        return f"c:maj"
    if 2 in interval_list and 5 in interval_list and 9 in interval_list:
        return f"d:min"
    if 4 in interval_list and 7 in interval_list and 11 in interval_list:
        return "e:min"
    if 5 in interval_list and 9 in interval_list and 0 in interval_list:
        return "f:maj"
    if 7 in interval_list and 11 in interval_list and 2 in interval_list:
        return "g:maj"
    if 9 in interval_list and 0 in interval_list and 4 in interval_list:
        return "a:min"
    if 11 in interval_list and 2 in interval_list and 5 in interval_list:
        return "b:dim"
    else: 
        return None

