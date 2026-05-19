import pytest
from Note import Note

def test_init_from_char():
    assert Note.init_from_char("A") == Note(69)
    
def test_get_interval():
    c4 = Note(60)
    d4 = Note(62)
    d5 = Note(74)
    # happy path
    assert Note.get_interval(c4, d4) == 2

    # higher note as first input
    assert Note.get_interval(d4, c4) == 2

    # wider than 1 octave, same result (for now)
    assert Note.get_interval(c4, d5) == 2