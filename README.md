# WhatTheChord
**Python library for real-time chord recognition from MIDI signals**

Real-time symbolic music chord recognition with music-theoretic priors.
Provides Python APIs for real-time MIDI parsing, chord identification,
and key-aware harmonic analysis.

## Demo Video

[![Demo Video](https://img.youtube.com/vi/j8TYpl-ZGOE/maxresdefault.jpg)](https://youtu.be/j8TYpl-ZGOE)

*Walkthrough of core functionality — chord recognition under different key contexts.*

## Key Characteristics

WhatTheChord encodes music theory directly into its analysis pipeline:

- **Key context awareness** — the same set of notes is analyzed differently
  under different key priors. A G major triad in C major surfaces as `V`;
  in A natural minor it surfaces as `VII`.
- **Top-k ambiguity preservation** — when input is genuinely ambiguous
  (e.g., a triad that could also be a 7th-chord shell), the system
  surfaces multiple plausible interpretations rather than forcing a
  single answer.
- **Music-theoretic position weighting** — 3rds and 7ths (chord-defining
  guide tones) carry more weight in template matching than roots and 5ths.
- **Jazz-default enharmonic spelling** — flats by default (Eb, Bb, Ab),
  per Real Book / iReal Pro convention.
- **Real-time MIDI ingestion** — thread-safe event buffer with sub-100ms
  recognition latency for live keyboard input.

## Installation

Requires Python 3.10+ and `uv` (or `pip`).

```bash
git clone https://github.com/hughkim/whatthechord.git
cd whatthechord
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Verify install:

```bash
uv run pytest
```

## Quick Start

### Real-time demo (requires MIDI keyboard)

```bash
uv run python examples/realtime_demo.py --key C major
```

Play chords on your MIDI keyboard. The terminal displays the top
interpretations with confidence scores and Roman numeral functions:

```
C3 E3 G3             -> Cmaj [I] 1.00 | Amin7 [vi7] 0.92 | Cmaj7 [Imaj7] 0.78
A4                   -> (no match)
E3 G3 A3 C4          -> Amin7 [vi7] 1.00
```

A few things worth noticing in this output:

- **`C3 E3 G3`** is unambiguously a C major triad — but the same notes
  are also the b3 + 5 + b7 of Am7 (root omitted), and the root + 3 + 5
  of Cmaj7 (7th omitted). The system surfaces all three with confidence
  gaps that reflect their musical plausibility.
- **`A4`** (a single note) returns no match — chord analysis requires
  at least two distinct pitch classes.
- **`E3 G3 A3 C4`** is Am7 in first inversion. The bass note (E)
  doesn't change the chord identity, only the inversion.

### Python API

```python
from whatthechord import harmony
from whatthechord.note import Note
from whatthechord.chord import Chord
from whatthechord.scale import Scale

# Build a Cmaj7 chord
chord = Chord([Note(60), Note(64), Note(67), Note(71)])  # C E G B

# Analyze in C major key context
key = Scale.from_name("C", "major")
results = harmony.analyze(chord, scale=key)

print(results[0])
# Cmaj7/inv0 [Imaj7] c=1.00

# Top-k alternatives reveal ambiguity
for r in results[:3]:
    print(r)
```

### Switching key context

The same chord changes interpretation under different keys:

```python
g_dom = Chord([Note(67), Note(71), Note(74), Note(77)])  # G B D F = G7

# In C major, G7 is V7
c_major = Scale.from_name("C", "major")
print(harmony.analyze(g_dom, scale=c_major)[0])
# G7 [V7] c=1.00

# In A natural minor, G7 is VII7 (NOT V — V would require harmonic minor)
a_minor = Scale.from_name("A", "minor")
print(harmony.analyze(g_dom, scale=a_minor)[0])
# G7 [VII7] c=1.00
```

## Architecture

### Module layout

```
src/whatthechord/
├── note.py           # MIDI value <-> pitch class, flat-default spelling
├── chord.py          # Container for a set of simultaneous Notes
├── scale.py          # Tonic + ScaleType, doubles as a key context
├── scale_type.py     # MAJOR / MINOR enum with interval tuples
├── harmony.py        # The analysis engine — analyze() returns ranked candidates
├── events.py         # Thread-safe EventBuffer for live MIDI streams
├── controller.py     # rtmidi callback dispatcher
└── midi_constants.py # Status bytes, key signature mappings
```

### Data flow

```
MIDI keyboard
    |
    v  (rtmidi callback thread)
MidiInputHandler
    |
    v
EventBuffer.on_note_on/off
    |
    v  <- main thread polls
buffer.get_active_notes()  ->  list[Note]
    |
    v
Chord.from_active_notes(notes)
    |
    v
harmony.analyze(chord, scale=key)
    |
    v
list[ChordAnalysis] sorted by confidence
```

### Key classes

- **`Note`** — A single MIDI note. Stores value (0-127), velocity, on/off
  timestamps. Pitch defaults to flat spelling; `pitch_sharp` available
  for sharp-key contexts.

- **`Chord`** — A set of simultaneous notes. Computes pitch-class set,
  bass note, and stores ranked `ChordAnalysis` candidates after analysis.

- **`Scale`** — A tonic + `ScaleType`. Doubles as a key context.
  Provides `degree_of()`, `diatonic_triad_quality()`,
  `diatonic_seventh_quality()`, and `roman_numeral()`.

- **`harmony.analyze()`** — The core function. Iterates all 12 pitch
  classes as candidate roots, matches against 9 quality templates
  (triads + 7th chords), applies key prior, returns ranked list.

- **`EventBuffer`** — Thread-safe single-source-of-truth for live MIDI.
  The same `Note` instance is referenced by both the historical event
  list and the active-notes index — updating one updates the other.

### Design decisions

- **Subset matching with position weights.** A chord matches a quality
  template if its pitch classes are a strict subset of the template's
  intervals (no foreign tones). Confidence is a weighted ratio where
  3rds and 7ths carry more weight (1.75) than roots and 5ths (1.0),
  reflecting their role as chord-defining guide tones.

- **Search all 12 roots, not just chord pitches.** Essential for shell
  voicings where the root is omitted. Two notes E + Bb only imply C7
  if we consider C as a candidate root despite C being absent.

- **Asymmetric key prior boosts.** Triads receive a stronger
  key-prior boost (`KEY_PRIOR_BOOST = 0.2`) than 7th chords
  (`KEY_PRIOR_BOOST_SEVENTH = 0.05`). The asymmetry encodes a musical
  fact: triads are atomic chord identities, while 7ths often appear
  as incomplete voicings in jazz, so over-boosting 7ths causes the
  algorithm to interpret every two-note pattern as some 7th-chord shell.

- **Top-k output.** When input is musically ambiguous (e.g., `F + C`
  could be Fmaj's root + 5th *or* Dm7's b3 + b7), the system returns
  multiple candidates with confidence gaps reflecting musical
  reasonableness, rather than forcing a single answer.

## Project Context

This library is part of a broader exploration of symbolic music
intelligence — interactive systems that can listen to and reason about
music as a player creates it. It draws on a dual background in music
performance (Berklee College of Music, Music Production & Engineering)
and computer science.

Real-time chord recognition is the foundation. Planned extensions form
a pipeline oriented toward interactive accompaniment and practice tools:

- **`whatthebeat`** *(next)* — meter and tempo induction from chord
  change patterns. Without an explicit click track, infer harmonic
  rhythm and beat phase from incoming events. Uses techniques from
  DTW / online alignment families.

- **`whatsnextchord`** *(planned)* — next-chord prediction conditioned on
  recent chord sequence, current metric position, and learned
  distributions over jazz/pop corpora. Combines symbolic
  representations from this library with sequence models trained on
  the Lakh MIDI Dataset.

Together: **listen -> identify -> locate in time -> predict.**

## Roadmap

- [x] Real-time chord recognition with key-aware analysis
- [x] Thread-safe MIDI event buffer
- [x] Music-theoretic Roman numeral function assignment (triads and 7ths)
- [ ] Evaluation suite with multi-label ground truth *(in progress)*
- [ ] `whatthebeat`: meter and tempo induction
- [ ] `whatsnextchord`: next-chord prediction trained on LMD
- [ ] Sustain pedal handling
- [ ] Section boundary detection

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

Built with [`python-rtmidi`](https://github.com/SpotlightKid/python-rtmidi).
Music-theoretic design choices draw from standard jazz harmony pedagogy.
