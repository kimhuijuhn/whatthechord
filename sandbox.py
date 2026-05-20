import sys
from mido import MidiFile

filename = sys.argv[1]
midi_file = MidiFile(filename)

midi_file.print_tracks()

