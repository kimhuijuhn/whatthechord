"""
Lead sheet representation as a chord sequence.

Score is the reference that ScoreFollower tracks against.
For MVP: simple chord symbol sequence. Beat durations and form
(verse/chorus structure) added in later versions.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScoreChord:
    """
    One chord position in a lead sheet.

    Attributes:
        root: pitch class 0-11
        quality: 'maj', 'min', 'maj7', '7', 'min7', 'hdim7', 'dim7', 'dim', 'aug'
        beats: duration in beats (default 4 = one bar in 4/4)
        bar_number: 1-indexed bar position (for display)
    """
    root: int
    quality: str
    beats: int = 4
    bar_number: Optional[int] = None

    def matches(self, other_root: int, other_quality: str) -> bool:
        """Identity match — used by DTW distance function."""
        return self.root == other_root and self.quality == other_quality

    def __repr__(self) -> str:
        from src.Note import NOTE_MAP
        name = NOTE_MAP[self.root]
        bar = f" (bar {self.bar_number})" if self.bar_number else ""
        return f"{name}{self.quality}{bar}"


@dataclass
class Score:
    """
    A lead sheet: ordered sequence of ScoreChords.

    For MVP: linear sequence (no repeats, no form structure).
    """
    chords: list[ScoreChord] = field(default_factory=list)
    title: str = ""
    tempo: int = 120  # BPM, for future timing-based features

    @classmethod
    def from_chord_strings(cls, chord_names: list[str], title: str = "") -> "Score":
        """
        Build a Score from a list of chord symbols like 'Cmaj7', 'Dm7', 'G7'.

        Format: <root><quality>
            'C', 'C#', 'Db', ..., 'B' for root
            '', 'maj7', 'm', 'min', 'm7', 'min7', '7', 'dim', 'dim7',
            'hdim7', 'm7b5', 'aug', '+' for quality

        Examples:
            'C'       → C maj triad
            'Cmaj7'   → C major 7th
            'Dm7'     → D minor 7th
            'G7'      → G dominant 7th
        """
        chords = []
        for i, name in enumerate(chord_names, start=1):
            root_pc, quality = _parse_chord_symbol(name)
            chords.append(ScoreChord(root=root_pc, quality=quality, bar_number=i))
        return cls(chords=chords, title=title)

    def __len__(self) -> int:
        return len(self.chords)

    def __getitem__(self, idx) -> ScoreChord:
        return self.chords[idx]


# -----------------------------------------------------------------------------
# Chord symbol parsing
# -----------------------------------------------------------------------------

# Quality string → internal quality name
_QUALITY_MAP = {
    "":      "maj",
    "^":     "maj",
    "maj":   "maj",
    "M":     "maj",
    "m":     "min",
    "min":   "min",
    "-":     "min",
    "maj7":  "maj7",
    "^7":    "maj7",
    "M7":    "maj7",
    "7":     "7",
    "m7":    "min7",
    "min7":  "min7",
    "-7":    "min7",
    "dim":   "dim",
    "°":     "dim",
    "dim7":  "dim7",
    "°7":    "dim7",
    "hdim7": "hdim7",
    "m7b5":  "hdim7",
    "ø":     "hdim7",
    "aug":   "aug",
    "+":     "aug",
}


def _parse_chord_symbol(symbol: str) -> tuple[int, str]:
    """
    Parse a chord symbol into (root_pc, quality).

    Raises ValueError on unparseable input.
    """
    from src.Note import NOTE_MAP, ENHARMONIC_SHARP

    symbol = symbol.strip()
    if not symbol:
        raise ValueError("empty chord symbol")

    # Try 2-char root first (C#, Db, etc.) then 1-char (C, D, ...)
    if len(symbol) >= 2 and symbol[1] in "#b":
        root_str, quality_str = symbol[:2], symbol[2:]
    else:
        root_str, quality_str = symbol[:1], symbol[1:]

    # Normalize enharmonic
    root_str = ENHARMONIC_SHARP.get(root_str, root_str)
    if root_str not in NOTE_MAP:
        raise ValueError(f"unknown root '{root_str}' in chord '{symbol}'")
    root_pc = NOTE_MAP.index(root_str)

    if quality_str not in _QUALITY_MAP:
        valid = sorted(set(_QUALITY_MAP.keys()))
        raise ValueError(f"unknown quality '{quality_str}' in chord '{symbol}'. Valid: {valid}")
    quality = _QUALITY_MAP[quality_str]

    return root_pc, quality