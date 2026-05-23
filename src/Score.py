"""
Lead sheet representation as a sequence of chord positions.

A Score is the reference that ScoreFollower tracks against. Each entry
represents one chord position with its bar/beat location and an
expression tag reserved for v2 iReal Pro protocol import (section
markers, repeat signs, etc.).
"""

from dataclasses import dataclass, field
from typing import NamedTuple


# -----------------------------------------------------------------------------
# Core data type
# -----------------------------------------------------------------------------

class ScoreEntry(NamedTuple):
    """
    One chord position in a lead sheet.

    Attributes:
        root: pitch class 0-11 (matches M2's ChordAnalysis.root)
        quality: chord quality string ('maj7', 'min7', '7', 'maj',
                 'min', 'dim', 'dim7', 'm7b5', 'aug') — same
                 vocabulary as M2's harmony module
        bar: 1-indexed bar number (preserves original lead sheet location)
        beat: beat within bar (1-4 in 4/4 time). For multi-chord bars,
              chords are distributed across beats (e.g., two chords →
              beats 1 and 3).
        expression: free-form tag for lead sheet metadata.
                    Reserved for v2 iReal Pro protocol import:
                    section markers ('section_A_start'), repeat signs
                    ('repeat_begin', 'repeat_end_first_ending'),
                    articulation ('fermata'), etc.
                    Currently always empty in MVP.
    """
    root: int
    quality: str
    bar: int
    beat: int
    expression: str = ""


# -----------------------------------------------------------------------------
# Score
# -----------------------------------------------------------------------------

@dataclass
class Score:
    """
    A lead sheet as an ordered sequence of ScoreEntry tuples.

    The entries list is linear playback order — repeats and other
    structural devices are unfolded during import (e.g., when reading
    iReal Pro chord charts), not modeled here.
    """
    entries: list[ScoreEntry] = field(default_factory=list)
    title: str = ""
    composer: str = ""
    tempo: int = 120  # BPM
    time_signature: tuple[int, int] = (4, 4)  # numerator, denominator

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    @classmethod
    def from_chord_strings(
        cls,
        chord_names: list[str],
        title: str = "",
        composer: str = "",
        tempo: int = 120,
    ) -> "Score":
        """
        Build a Score from chord symbols, one per bar starting at beat 1.

        Single-chord-per-bar convenience constructor. For lead sheets
        with multiple chords per bar (common in jazz), use from_bars().

        Args:
            chord_names: list of chord symbols ('Cmaj7', 'Dm7', 'G7', etc.)
                         Both flat (Eb, Bb) and sharp (D#, A#) spellings
                         are accepted; internally normalized to flats.
            title: lead sheet title
            composer: composer name
            tempo: BPM

        Example:
            Score.from_chord_strings(["Cmaj7", "Dm7", "G7", "Cmaj7"])
        """
        entries = []
        for i, name in enumerate(chord_names, start=1):
            root, quality = _parse_chord_symbol(name)
            entries.append(ScoreEntry(root=root, quality=quality, bar=i, beat=1))
        return cls(entries=entries, title=title, composer=composer, tempo=tempo)

    @classmethod
    def from_bars(
        cls,
        bars: list[str],
        title: str = "",
        composer: str = "",
        tempo: int = 120,
        time_signature: tuple[int, int] = (4, 4),
    ) -> "Score":
        """
        Build a Score from bar strings, supporting multiple chords per bar.

        Each bar is a space-separated string of chord symbols. Chords
        within a bar are distributed evenly across the bar's beats.

        Args:
            bars: list of bar strings. Each is space-separated chords.
                  '' (empty string) means: hold previous chord through this bar.
            title, composer, tempo, time_signature: lead sheet metadata

        Examples:
            "Cmaj7"           → one chord on beat 1
            "Dm7 G7"          → Dm7 on beat 1, G7 on beat 3 (in 4/4)
        """
        beats_per_bar = time_signature[0]
        entries = []

        for bar_idx, bar_str in enumerate(bars, start=1):
            chord_symbols = bar_str.split()
            if not chord_symbols:
                continue

            n = len(chord_symbols)
            for chord_idx, sym in enumerate(chord_symbols):
                root, quality = _parse_chord_symbol(sym)
                # Distribute evenly: chord_idx-th of n chords starts at
                # beat = 1 + (chord_idx * beats_per_bar / n)
                beat = 1 + int(chord_idx * beats_per_bar / n)
                entries.append(ScoreEntry(
                    root=root, quality=quality, bar=bar_idx, beat=beat,
                ))

        return cls(
            entries=entries,
            title=title,
            composer=composer,
            tempo=tempo,
            time_signature=time_signature,
        )

    # -------------------------------------------------------------------------
    # Container interface
    # -------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, idx) -> ScoreEntry:
        return self.entries[idx]

    def __iter__(self):
        return iter(self.entries)

    def __repr__(self) -> str:
        head = self.title if self.title else f"Score ({len(self)} entries)"
        return f"Score({head!r}, {len(self)} entries, {self.tempo} BPM)"


# -----------------------------------------------------------------------------
# Chord symbol parsing
# -----------------------------------------------------------------------------

# Quality string → internal quality name (matches M2 vocabulary)
_QUALITY_MAP = {
    # Triads
    "":      "maj",
    "maj":   "maj",
    "M":     "maj",
    "m":     "min",
    "min":   "min",
    "-":     "min",
    "dim":   "dim",
    "°":     "dim",
    "aug":   "aug",
    "+":     "aug",
    # Sevenths
    "maj7":  "maj7",
    "M7":    "maj7",
    "^7":    "maj7",   # iReal Pro convention
    "7":     "7",
    "m7":    "min7",
    "min7":  "min7",
    "-7":    "min7",   # iReal Pro convention
    "dim7":  "dim7",
    "°7":    "dim7",
    "m7b5": "m7b5",
    "m7b5":  "m7b5",
    "-7b5":  "m7b5",  # iReal Pro convention
    "ø":     "m7b5",
    "ø7":    "m7b5",
}


def _parse_chord_symbol(symbol: str) -> tuple[int, str]:
    """
    Parse a chord symbol into (root_pc, quality).

    Recognizes both common notation (Cmaj7, Dm7, G7) and iReal Pro
    notation (C^7, D-7, G7). Both flat (Eb, Bb) and sharp (D#, A#)
    spellings accepted; internally normalized to flats (jazz convention).
    """
    from src.Note import NOTE_MAP, ENHARMONIC_FLAT

    symbol = symbol.strip()
    if not symbol:
        raise ValueError("empty chord symbol")

    # 2-char root (Eb, Bb, C#, etc.) first, then 1-char (C, D, ...)
    if len(symbol) >= 2 and symbol[1] in "#b":
        root_str, quality_str = symbol[:2], symbol[2:]
    else:
        root_str, quality_str = symbol[:1], symbol[1:]

    # Normalize sharp input to flat (the canonical jazz form)
    root_str = ENHARMONIC_FLAT.get(root_str, root_str)
    if root_str not in NOTE_MAP:
        raise ValueError(f"unknown root '{root_str}' in chord '{symbol}'")
    root_pc = NOTE_MAP.index(root_str)

    if quality_str not in _QUALITY_MAP:
        valid = sorted(set(_QUALITY_MAP.keys()) - {""})
        raise ValueError(
            f"unknown quality '{quality_str}' in chord '{symbol}'. "
            f"Valid qualities: {valid}"
        )
    quality = _QUALITY_MAP[quality_str]

    return root_pc, quality