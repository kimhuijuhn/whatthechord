import sys
import time
import argparse
from rtmidi import midiutil

from src.events import EventBuffer
from src.controller import MidiInputHandler
from src.Chord import Chord
from src.Scale import Scale
from src import harmony

def format_chord_display(chord: Chord, top_n: int = 3) -> str:
    """ Format top N chord analyses for terminal display. """
    if chord.is_empty:
        return "-"
    
    notes_str = " ".join(str(n) for n in chord.notes)
    if not chord.analyses:
        return f"{notes_str} -> (no match)"
    
    candidates = chord.analyses[:top_n]
    candidates_str = " | ".join(
        f"{c.root_name}{c.quality}"
        + (f" [{c.function}]" if c.function else "")
        + f" {c.confidence:.2f}"
        for c in candidates
    )
    return f"{notes_str:20s} -> {candidates_str}"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time MIDI chord detection with key-aware analysis.",
        epilog="Example: python main.py --key C major"
    )
    parser.add_argument(
        "--key",
        nargs=2,
        metavar=("TONIC", "MODE"),
        default=["C", "major"],
        help="Key context as TONIC MODE (e.g., 'C major', 'A minor'). "
             "Default: C major.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="MIDI input port index (default: 0).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=3,
        help="Number of candidate interpretations to display (default: 3).",
    )
    return parser.parse_args()

def main():
    args = parse_args()

    midiin, portname = midiutil.open_midiport(0)
    print(f"Current Port: {portname}")

    # Listen to incoming MIDI messages
    buffer = EventBuffer()
    handler = MidiInputHandler(buffer)
    midiin.set_callback(handler)

    # temporary key settings
    #TODO: maybe take in sysargv? 
    key = Scale.from_name(args.key[0], args.key[1])
    print(f"Key: {key}\t Play chords from MIDI Controller (Ctrl+C to exit)")


    # main loop
    last_output = ""
    try:
        while True:
            active = buffer.get_active_notes()
            chord = Chord.from_active_notes(active)
            harmony.analyze(chord, scale=key)
            output = format_chord_display(chord, top_n=args.top_n)
            if output != last_output:
                print(f"\r{output:<120}", end="", flush=True)
                last_output = output
            time.sleep(0.05)  # 20Hz `display refresh

    except KeyboardInterrupt:
        print(f"\nSession ended. Total notes: {len(buffer)}")
        midiin.close_port()

if __name__ == "__main__":
    main()