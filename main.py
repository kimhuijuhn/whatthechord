from rtmidi import midiutil
import midi_listener

def main():
    midiin, portname = midiutil.open_midiport(0)
    print("Current Port: ", portname)
    midi_listener.print_current_on_notes(midiin)

if __name__ == "__main__":
    main()