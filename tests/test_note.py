from src.Note import Note

c4 = Note(60)
d4 = Note(62)
d5 = Note(74)

def test_from_pitch():
    assert Note.from_pitch("C", 4).has_same_pitch(c4)
    
def test_get_interval():

    # happy path
    assert Note.get_interval(c4, d4) == 2

    # higher note as first input
    assert Note.get_interval(d4, c4) == 2

    # wider than 1 octave, same result (for now)
    assert Note.get_interval(c4, d5) == 2