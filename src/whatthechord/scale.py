from dataclasses import dataclass
from .note import NOTE_MAP, ENHARMONIC_FLAT
from .scale_type import ScaleType
from .midi_constants import KEY_SIGNATURE_TO_TONIC


@dataclass(frozen=True)
class Scale:
    """
    A scale with a tonic — a concrete realization of abstract ScaleType.

    Serves dual purpose: represents both a scale (set of pitches) and a
    musical key (tonal center). Modal context (e.g., D dorian within
    C major) would require a separate class; not yet supported.

    Note spellings default to flats (Eb, Bb, Ab, Db) — the convention
    in jazz lead sheets.

    Frozen for hashability purposes.
    """

    tonic: int
    scale_type: ScaleType


    def __post_init__(self):
        if not (0 <= self.tonic < 12):
            raise ValueError(f"tonic must be 0-11, got {self.tonic}")


    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    @classmethod
    def from_name(cls, tonic_str: str, scale_str: str = "MAJOR") -> "Scale":
        """
        Construct from human-readable names.

        Args:
            tonic_str: 'C', 'Eb', 'Bb', etc. Sharp spellings (D#, A#, etc.)
                       are normalized to flats via ENHARMONIC_FLAT.
            scale_str: 'MAJOR', 'major', 'IONIAN', etc. Case-insensitive.

        Examples:
            Scale.from_name("Eb", "major")    # F blues, jazz standard key
            Scale.from_name("D#", "major")    # same key, sharp spelling input
            Scale.from_name("Bb")             # default major
        """
        # Normalize sharp input to flat (the canonical form)
        tonic_str = ENHARMONIC_FLAT.get(tonic_str, tonic_str)
        if tonic_str not in NOTE_MAP:
            raise ValueError(f"unknown tonic '{tonic_str}'")

        try:
            scale_type = ScaleType[scale_str.upper()]
        except KeyError:
            valid = [st.name for st in ScaleType]
            raise ValueError(f"unknown mode '{scale_str}'. Valid: {valid}")

        return cls(tonic=NOTE_MAP.index(tonic_str), scale_type=scale_type)

    @classmethod
    def from_midi_key_signature(cls, sharps_or_flats: int, mode_flag: int) -> "Scale":
        """
        Parse MIDI Key Signature meta message into a Scale.

        sharps_or_flats: -7 to +7 (negative = flats, positive = sharps)
        mode_flag: 0 = major, 1 = minor (natural minor by MIDI convention)
        """
        if sharps_or_flats not in KEY_SIGNATURE_TO_TONIC:
            raise ValueError(f"sharps_or_flats out of range: {sharps_or_flats}")

        major_tonic = KEY_SIGNATURE_TO_TONIC[sharps_or_flats]
        if mode_flag == 0:
            return cls(tonic=major_tonic, scale_type=ScaleType.MAJOR)
        else:
            return cls(tonic=(major_tonic - 3) % 12, scale_type=ScaleType.MINOR)


    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def tonic_name(self) -> str:
        """
        Flat-spelled tonic name (e.g., 'Eb', 'Bb'). Default jazz convention.

        For sharp-spelled name, use NOTE_MAP_SHARP[self.tonic] directly.
        """
        return NOTE_MAP[self.tonic]

    @property
    def mode(self) -> str:
        """Lowercase scale-type name, e.g., 'major', 'minor'."""
        return self.scale_type.name.lower()

    @property
    def intervals(self) -> tuple[int, ...]:
        return self.scale_type.intervals

    @property
    def num_degrees(self) -> int:
        return self.scale_type.num_degrees

    @property
    def pitch_classes(self) -> frozenset[int]:
        """The pitch classes belonging to this scale."""
        return frozenset((self.tonic + i) % 12 for i in self.intervals)


    # -------------------------------------------------------------------------
    # Queries
    # -------------------------------------------------------------------------

    def is_diatonic(self, pitch_class: int) -> bool:
        return pitch_class in self.pitch_classes

    def degree_of(self, pitch_class: int) -> int | None:
        """
        Scale degree (1-N) of the given pitch class, or None if non-diatonic.
        """
        offset = (pitch_class - self.tonic) % 12
        if offset in self.intervals:
            return self.intervals.index(offset) + 1
        return None

    def diatonic_triad_pitches(self, degree: int) -> tuple[int, int, int]:
        """
        Pitch classes (0-11) of the diatonic triad on the given scale degree.

        The triad is built by stacking thirds: take the degree-th scale note
        as root, skip one to get the third, skip one more for the fifth.
        The chord wraps around the scale if necessary (e.g., the V triad in
        C major: G-B-D, where D wraps from scale position 8 back to 1).

        Returns pitch classes (0-11), octave-independent.

        Args:
            degree: 1 to num_degrees.

        Example:
            >>> c_major = Scale.from_name("C", "major")
            >>> c_major.diatonic_triad_pitches(5)
            (7, 11, 2)   # G, B, D — the V chord
        """
        n = self.num_degrees
        if not (1 <= degree <= n):
            raise ValueError(f"degree must be 1-{n}, got {degree}")

        # Convert 1-indexed degree to 0-indexed scale position
        root_position = degree - 1

        # Stack thirds: root, root+2 (third), root+4 (fifth)
        # Modulo num_degrees to wrap around the scale
        scale_positions = [(root_position + step) % n for step in (0, 2, 4)]

        # Convert scale positions to absolute pitch classes
        return tuple(
            (self.tonic + self.intervals[pos]) % 12
            for pos in scale_positions
        )

    def diatonic_triad_quality(self, degree: int) -> str:
        """Returns 'maj', 'min', 'dim', 'aug', or 'unknown'."""
        pcs = self.diatonic_triad_pitches(degree)
        root = pcs[0]
        intervals = tuple(sorted((p - root) % 12 for p in pcs))
        return {
            (0, 4, 7): "maj",
            (0, 3, 7): "min",
            (0, 3, 6): "dim",
            (0, 4, 8): "aug",
        }.get(intervals, "unknown")

    def roman_numeral(self, degree: int) -> str:
        """
        Roman numeral for a diatonic triad on the given degree.
        Uppercase = major/aug, lowercase = min/dim, ° suffix = dim.
        Does not yet support non-diatonic chords.
        """
        numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
        n = self.num_degrees
        if not (1 <= degree <= n):
            raise ValueError(f"degree must be 1-{n}, got {degree}")
        quality = self.diatonic_triad_quality(degree)
        symbol = numerals[degree - 1]
        if quality == "min":
            return symbol.lower()
        elif quality == "dim":
            return symbol.lower() + "°"
        elif quality == "aug":
            return symbol + "+"
        else:
            return symbol

    def __repr__(self) -> str:
        return f"Scale({self.tonic_name} {self.mode})"