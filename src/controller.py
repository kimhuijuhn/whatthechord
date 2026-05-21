
import time
from .Note import Note
from . import chordgrammar as cg
from .Timestamp import Timestamp

MIDI_ON = 144
MIDI_OFF = 128

def print_current_on_notes(midiin):
    """ Print list of currently ON notes based on message """
    active_notes = []
    timestamp = Timestamp()
    log = []

    try:
        while True:
            timestamp.start()
            msg = midiin.get_message()
            if msg:
                status = msg[0][0]
                note = Note(msg[0][1])

                # store a new ON note
                if status == MIDI_ON and note not in active_notes:
                    note.set_on_time(timestamp.capture())
                    active_notes.append(note)

                # discard OFF note and store it on log
                if status == MIDI_OFF and note in active_notes:
                    to_log = active_notes[active_notes.index(note)]
                    to_log.set_off_time(timestamp.capture())
                    log.append(to_log)
                    active_notes.remove(note)

                # print current ON notes
                print(f"{active_notes}".ljust(40), end="\r", flush=True)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        midiin.close_port()

    print("Note\tStart\tDuration")
    for note in log:
        print(f"{note}\t{note.on_time:2f}\t{(note.off_time - note.on_time):2f}")