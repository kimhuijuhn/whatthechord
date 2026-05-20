#TODO: add timestamp information

import time
from .Note import Note
from . import chordgrammar as cg

def print_current_on_notes(midiin):
    """ Print list of currently ON notes based on message """
    current_notes = []

    try:
        while True:
            msg = midiin.get_message()
            if msg:
                status = msg[0][0]
                note = Note(msg[0][1])

                # store a new ON note
                if status == 144 and note not in current_notes:
                    current_notes.append(note)

                # discard OFF note
                if status == 128 and note in current_notes:
                    current_notes.remove(note)

                # print current ON notes
                print(f"{current_notes}".ljust(40), end="\r", flush=True)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        midiin.close_port()