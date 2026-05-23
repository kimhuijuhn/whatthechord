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
    
    def diatonic_seventh_quality(self, degree: int) -> str:
        """
        Returns the diatonic 7th chord quality on a given scale degree.

        Computed by combining the diatonic triad with the actual 7th scale
        degree above the root — not by mapping triad quality to 7th quality.
        This correctly handles natural minor's VII (G in A minor → G7, not
        Gmaj7), Mixolydian-like contexts, etc.

        Returns: 'maj7', '7', 'min7', 'm7b5', 'dim7', or 'unknown'.

        Example:
            >>> Scale.from_name("C", "major").diatonic_seventh_quality(5)
            '7'   # G7 (dominant)
            >>> Scale.from_name("A", "minor").diatonic_seventh_quality(7)
            '7'   # G7 (VII7, not maj7)
        """
        n = self.num_degrees
        if not (1 <= degree <= n):
            raise ValueError(f"degree must be 1-{n}, got {degree}")

        triad_pcs = self.diatonic_triad_pitches(degree)
        root_pc = triad_pcs[0]

        # 7th = the 7th scale position from this degree (6 steps up)
        seventh_pos = (degree - 1 + 6) % n
        seventh_pc = (self.tonic + self.intervals[seventh_pos]) % 12

        intervals_from_root = tuple(sorted(
            (pc - root_pc) % 12 for pc in (*triad_pcs, seventh_pc)
        ))
        return {
            (0, 4, 7, 11): "maj7",
            (0, 4, 7, 10): "7",
            (0, 3, 7, 10): "min7",
            (0, 3, 6, 10): "m7b5",
            (0, 3, 6, 9):  "dim7",
        }.get(intervals_from_root, "unknown")

    def roman_numeral(self, degree: int, is_seventh: bool = False) -> str:
        """
        Roman numeral for a diatonic chord on the given degree.

        Uppercase = major-quality root triad, lowercase = minor/diminished.
        Suffix indicates extension:
            triad: '°' = dim, '+' = aug
            7th:   '7' suffix, 'maj7' for major 7, 'ø7' for half-diminished

        Args:
            degree: 1 to num_degrees.
            is_seventh: if True, returns 7th chord Roman (e.g., 'V7', 'iiø7').

        Examples:
            >>> C = Scale.from_name("C", "major")
            >>> C.roman_numeral(5)                # 'V'
            >>> C.roman_numeral(5, is_seventh=True)  # 'V7'
            >>> C.roman_numeral(7, is_seventh=True)  # 'viiø7'
            >>> Am = Scale.from_name("A", "minor")
            >>> Am.roman_numeral(7, is_seventh=True) # 'VII7' (not maj7!)
        """
        numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
        n = self.num_degrees
        if not (1 <= degree <= n):
            raise ValueError(f"degree must be 1-{n}, got {degree}")

        symbol = numerals[degree - 1]

        if not is_seventh:
            quality = self.diatonic_triad_quality(degree)
            if quality == "min":
                return symbol.lower()
            elif quality == "dim":
                return symbol.lower() + "°"
            elif quality == "aug":
                return symbol + "+"
            else:
                return symbol
        else:
            quality = self.diatonic_seventh_quality(degree)
            if quality == "maj7":
                return symbol + "maj7"
            elif quality == "7":
                return symbol + "7"
            elif quality == "min7":
                return symbol.lower() + "7"
            elif quality == "m7b5":
                return symbol.lower() + "ø7"
            elif quality == "dim7":
                return symbol.lower() + "°7"
            else:
                return symbol + "?"
            
    def __repr__(self) -> str:
        return f"Scale({self.tonic_name} {self.mode})"