from .note import Note

class Chord:
    """
    A class representing a set of notes without harmonic interpretations.

    Harmonic analysis is computed by harmony module called by 
    self.analyze. Multiple analyses may exist in one Chord due to harmonic 
    polysemy.

    Attributes:
        notes(list[Note])
    """


    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    def __init__(self, notes:list[Note]):
        """ store distinct Notes sorted low to high. """
        seen = set()
        unique = []
        for n in notes:
            if n.value not in seen:
                seen.add(n.value)
                unique.append(n)
        self.notes = sorted(unique, key=lambda n: n.value)

        # analyses are empty until filled
        self.analyses = []

    @classmethod
    def from_active_notes(cls, active_notes:list[Note]):
        """ Snapshot from EventBuffer.get_active_notes() """
        return cls(active_notes)
    
    @classmethod
    def from_recent_notes(cls, recent_notes:list[Note]):
        """ Windowed view from EventBuffer.get_recent_notes() """
        return cls(recent_notes)
    

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    @property
    def pitch_classes(self) -> set[int]:
        """ Distinct MIDI values mod 12 within a Chord. """
        return {n.value % 12 for n in self.notes}
    
    @property
    def bass(self) -> Note | None:
        """ The lowest note in a Chord. """
        return self.notes[0] if self.notes else None

    @property
    def is_empty(self) -> bool:
        return len(self.notes) == 0

    @property
    def is_analyzable(self) -> bool:
        """ At least 2 distince pitch classes to derive ChordAnalysis. """
        return len(self.pitch_classes) > 1
    

    # -------------------------------------------------------------------------
    # Special Methods
    # -------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.notes)

    def __repr__(self) -> str:
        if not self.analyses:
            return f"Chord({[str(n) for n in self.notes]})"
        top = self.analyses[0]
        return f"Chord({top}, +{len(self.analyses)-1} alts)"