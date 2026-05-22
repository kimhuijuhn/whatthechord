from dataclass import dataclass
from Note import NOTE_MAP
from Scale import Scale, SCALES


@dataclass(frozen=True)
class KeySignature:
    """
    Representation of a key signature (tonic pitch class + scale).
    Frozen for hashability.

    """
    tonic: int  # pitch class (MIDI value % 12)
    scale: Scale

    def __post_init__(self):
        if not (0 <= self.tonic < 12):
            raise ValueError(f"Tonic must be 0-11, got {self.tonic}")
        
    

# -----------------------------------------------------------------------------
# Constructors
# -----------------------------------------------------------------------------

