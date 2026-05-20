import pytest
from src.Note import Note
from src.Scale import Scale

c4 = Note(60)
d4 = Note(62)
e4 = Note(64)
f4 = Note(65)
g4 = Note(67)
a4 = Note(69)
b4 = Note(71)
cmaj_list = [c4, e4, g4]
dmin_list = [d4, f4, a4]
emin_list = [e4, g4, b4]
fmaj_list = [f4, a4, c4]
gmaj_list = [g4, b4, d4]
amin_list = [a4, c4, e4]
bdim_list = [b4, d4, f4]

def test_init():
    c_maj_scale = Scale(c4.pitch)
    assert c_maj_scale.root == "C"
    assert c_maj_scale.mode == "ionian"
    assert c_maj_scale.notes == [
        ("C", "maj"), ("D", "min"), ("E", "min"), ("F", "maj"), ("G", "maj"),
        ("A", "min"), ("B", "dim")
    ]