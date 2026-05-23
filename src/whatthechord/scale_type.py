from enum import Enum


class ScaleType(Enum):
    """
    Abstract scale patterns — interval sequences from tonic.

    Alias pairs (same interval pattern, different names):
      MAJOR == IONIAN
      MINOR == AEOLIAN

    MAJOR/MINOR are canonical (used in .name); IONIAN/AEOLIAN are aliases.
    """

    MAJOR = (0, 2, 4, 5, 7, 9, 11)
    IONIAN = (0, 2, 4, 5, 7, 9, 11)    # alias of MAJOR
    MINOR = (0, 2, 3, 5, 7, 8, 10)     # natural minor
    AEOLIAN = (0, 2, 3, 5, 7, 8, 10)   # alias of MINOR
    DORIAN = (0, 2, 3, 5, 7, 9, 10)
    PHRYGIAN = (0, 1, 3, 5, 7, 8, 10)
    LYDIAN = (0, 2, 4, 6, 7, 9, 11)
    MIXOLYDIAN = (0, 2, 4, 5, 7, 9, 10)
    LOCRIAN = (0, 1, 3, 5, 6, 8, 10)
    HARMONIC_MINOR = (0, 2, 3, 5, 7, 8, 11)
    MELODIC_MINOR = (0, 2, 3, 5, 7, 9, 11)

    @property
    def intervals(self) -> tuple[int, ...]:
        return self.value

    @property
    def num_degrees(self) -> int:
        return len(self.value)

    def __repr__(self) -> str:
        return f"ScaleType.{self.name}"