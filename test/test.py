import pytest
import src.chordgrammar as cg
from src.Note import Note

def test_detect_primary_chords():
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

    assert cg.detect_primary_triad(cmaj_list, 'C') == 'c:maj'
    assert cg.detect_primary_triad(dmin_list, 'C') == 'd:min'
    assert cg.detect_primary_triad(emin_list, 'C') == 'e:min'
    assert cg.detect_primary_triad(fmaj_list, 'C') == 'f:maj'
    assert cg.detect_primary_triad(gmaj_list, 'C') == 'g:maj'
    assert cg.detect_primary_triad(amin_list, 'C') == 'a:min'
    assert cg.detect_primary_triad(bdim_list, 'C') == 'b:dim'