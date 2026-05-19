from rtmidi import midiutil
import sandbox

def main():
    midiin, portname = midiutil.open_midiport(0)
    print("Current Port: ", portname)
    sandbox.get_current_on_notes(midiin)

if __name__ == "__main__":
    main()