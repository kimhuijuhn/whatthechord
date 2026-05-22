"""
Harmonic analysis: identify the harmonic identity of a Chord.

Core function:
    analyze(chord, scale=None) -> list[ChordAnalysis]

Returns all plausible interpretations of the chord, sorted by confidence.
A single Chord may have multiple ChordAnalysis instances when the note
set is ambiguous (e.g., diminished 7th has 4 enharmonic rotations).

When a Scale is provided, diatonic interpretations receive a confidence
boost and have their Roman numeral function set.
"""

from dataclasses import dataclass
from .Note import NOTE_MAP
from .Chord import Chord
from .Scale import Scale


# -----------------------------------------------------------------------------
# Hyperparameters
# -----------------------------------------------------------------------------

# Quality templates: ordered intervals from root (semitones).
# Position in tuple = chord tone role (0=root, 1=3rd, 2=5th, 3=7th).
# This ordering aligns with POSITION_WEIGHTS below.
QUALITY_TEMPLATES: dict[str, tuple[int, ...]] = {
    # Triads
    "maj":   (0, 4, 7),
    "min":   (0, 3, 7),
    "dim":   (0, 3, 6),
    "aug":   (0, 4, 8),
    # Sevenths
    "maj7":  (0, 4, 7, 11),
    "7":     (0, 4, 7, 10),
    "min7":  (0, 3, 7, 10),
    "hdim7": (0, 3, 6, 10),
    "dim7":  (0, 3, 6, 9),
}

# Music-theoretic salience for each chord tone position.
# 3rd defines major/minor identity. 7th defines extension identity.
# Root and 5th are more often omitted in voicings.
# Default values are theory-motivated; tunable via labeled evaluation.
DEFAULT_POSITION_WEIGHTS: tuple[float, ...] = (1.0, 1.75, 1.0, 1.75)

# Additive bonus to confidence for chords diatonic to the given scale.
KEY_PRIOR_BOOST: float = 0.2


# -----------------------------------------------------------------------------
# Data class
# -----------------------------------------------------------------------------

@dataclass
class ChordAnalysis:
    """
    One interpretation of a Chord's harmonic identity. 

    A single Chord may have multiple ChordAnalysis instances when the
    note set is ambiguous (dim7 rotations, power chord with multiple
    plausible roots, etc.).
    """
    root: int                           # pitch class 0-11
    quality: str                        # chord qualities like maj, min
    inversion: int                      # 0 = root, 1 = 1st, 2 = 2nd, 3 = 3rd
    function: str | None = None      # Roman numeral if scale provided
    confidence: float = 0.0

    @property
    def root_name(self) -> str:
        return NOTE_MAP[self.root]

    def __repr__(self) -> str:
        fn = f" [{self.function}]" if self.function else ""
        inv = f"/inv{self.inversion}" if self.inversion > 0 else ""
        return f"{self.root_name}{self.quality}{inv}{fn} c={self.confidence:.2f}"


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def analyze(chord: Chord, scale: Scale | None = None,
            position_weights: tuple[float, ...] | None = None
            ) -> list[ChordAnalysis]:
    """
    Identify the most plausible harmonic interpretations of a chord.

    Args:
        chord: The chord to analyze.
        scale: Optional key context. When provided, diatonic interpretations
               receive a confidence boost and Roman numeral functions are set.
        position_weights: Override the default POSITION_WEIGHTS. Used for
                          hyperparameter sweeps. If None, uses module default.

    Returns:
        List of ChordAnalysis candidates, sorted by confidence (descending).
        Empty if the chord is not analyzable or matches no template.

    Side effect:
        Sets chord.analyses to the returned list.
    """

    if position_weights is None:
        position_weights = DEFAULT_POSITION_WEIGHTS

    if not chord.is_analyzable:
        chord.analyses = []
        return []

    candidates: list[ChordAnalysis] = []
    pitch_classes = chord.pitch_classes
    bass_pc = chord.bass.value % 12

    # Try every possible pitch class as root, not just those present in chord.
    # This is necessary for incomplete voicings where the root is omitted
    # (e.g., jazz shell voicing E+Bb implies C7 even though C is absent).
    for root_pc in range(12):
        # Intervals from this candidate root, normalized
        intervals = tuple(sorted((pc - root_pc) % 12 for pc in pitch_classes))

        # Try matching against each quality template
        for quality, template in QUALITY_TEMPLATES.items():
            confidence = _template_match_score(intervals, template, 
                                            position_weights=position_weights)
            if confidence == 0.0:
                continue

            inversion = _inversion_from_bass(root_pc, bass_pc, template)
            candidates.append(ChordAnalysis(
                root=root_pc,
                quality=quality,
                inversion=inversion,
                confidence=confidence,
            ))

    if scale is not None:
        _apply_key_prior(candidates, scale)

    candidates.sort(key=lambda c: c.confidence, reverse=True)
    chord.analyses = candidates
    return candidates


# -----------------------------------------------------------------------------
# Internal scoring
# -----------------------------------------------------------------------------

def _template_match_score(
    chord_intervals: tuple[int, ...],
    template: tuple[int, ...],
    position_weights: tuple[float, ...] = DEFAULT_POSITION_WEIGHTS,
) -> float:
    """
    Weighted ratio of template tones present in the chord.

    Exact subset required: chord must not contain any pitch outside the
    template (no foreign tones). Returns 0.0 if violated.

    Otherwise: sum(weights of present chord tones) / sum(template weights).
    """
    chord_set = set(chord_intervals)
    template_set = set(template)

    # Reject if chord has any pitch outside the template
    if not chord_set.issubset(template_set):
        return 0.0

    # Weighted sum over template positions
    matched_weight = sum(
        position_weights[i]
        for i, interval in enumerate(template)
        if interval in chord_set
    )
    total_weight = sum(position_weights[:len(template)])

    return matched_weight / total_weight


def _inversion_from_bass(
    root_pc: int,
    bass_pc: int,
    template: tuple[int, ...],
) -> int:
    """
    Determine inversion from bass note's position in the template.

    Returns the index of the bass interval within the template:
        0 = root in bass (root position)
        1 = third in bass (first inversion)
        2 = fifth in bass (second inversion)
        3 = seventh in bass (third inversion)
    """
    bass_offset = (bass_pc - root_pc) % 12
    if bass_offset in template:
        return template.index(bass_offset)
    return 0  # fallback: bass not a chord tone (shouldn't occur for subset matches)


def _apply_key_prior(candidates: list[ChordAnalysis], scale: Scale) -> None:
    """
    For each candidate whose root and quality match a diatonic triad of
    the scale, boost confidence and assign the Roman numeral function.

    Mutates candidates in place. Non-diatonic candidates are unchanged.

    Note: Only triad qualities (maj/min/dim/aug) are matched against
    diatonic positions; seventh chords are left untouched here.
    Borrowed chords (e.g., V major in minor key) also not handled —
    future work.
    """
    triad_qualities = {"maj", "min", "dim", "aug"}

    for c in candidates:
        if c.quality not in triad_qualities:
            continue

        degree = scale.degree_of(c.root)
        if degree is None:
            continue

        diatonic_quality = scale.diatonic_triad_quality(degree)
        if c.quality == diatonic_quality:
            c.confidence = min(1.0, c.confidence + KEY_PRIOR_BOOST)
            c.function = scale.roman_numeral(degree)