from .Note import Note
from .Scale import Scale, MODES
from .Chord import Chord

#TODO: we can detect C major triad in root form

def determine_chord_quality(chord:Chord, key: str = "C"):
        """ determine chord quality given a list of notes. """
        # implement triads first, develop later
        pass