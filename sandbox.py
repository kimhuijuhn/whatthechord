import time
from Note import Note

def get_current_on_notes(midiin):
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
                print(current_notes)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        midiin.close_port()

def detect_primary_triad(note_list, key):
    interval_list = [
        Note.get_interval(n, Note.init_from_char(key, 0)) for n in note_list]

    # I
    if 0 in interval_list and 4 in interval_list and 7 in interval_list:
        return "c:maj"

    # ii
    if 2 in interval_list and 5 in interval_list and 9 in interval_list:
        return "d:min"

    # iii
    if 4 in interval_list and 7 in interval_list and 11 in interval_list:
        return "e:min"

    # iv
    if 5 in interval_list and 9 in interval_list and 0 in interval_list:
        return "f:maj"

    # V
    if 7 in interval_list and 11 in interval_list and 2 in interval_list:
        return "g:maj"

    # vi
    if 9 in interval_list and 0 in interval_list and 4 in interval_list:
        return "a:min"

    # vii
    if 11 in interval_list and 2 in interval_list and 5 in interval_list:
        return "b:dim"

    else: 
        return None