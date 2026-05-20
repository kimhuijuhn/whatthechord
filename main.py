from rtmidi import midiutil
from src import controller

def main():
    midiin, portname = midiutil.open_midiport(0)
    print("Current Port: ", portname)
    controller.print_current_on_notes(midiin)

if __name__ == "__main__":
    main()