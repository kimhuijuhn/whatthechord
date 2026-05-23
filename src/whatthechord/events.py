import threading
import time
from .note import Note

class EventBuffer:
    """
    Thread-safe buffer of Note instances.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._notes: list[Note] = []
        self._active_notes: dict[int, Note] = {}
        self._session_start = time.perf_counter()

    def now(self) -> float:
        return time.perf_counter() - self._session_start
    

    # -------------------------------------------------------------------------
    # Producer Methods
    # -------------------------------------------------------------------------

    def on_note_on(self, midi_value: int, velocity: int = 64):
        """ 
        Add note to _notes and _active_notes. 
        if note is retriggered, set off_time and then start again. 
        """

        with self._lock:
            t = self.now()

            # if same note retriggered, close the note and restart
            if midi_value in self._active_notes:
                self._active_notes[midi_value].set_off_time(t)

            note = Note(midi_value, velocity)
            note.set_on_time(t)
            self._notes.append(note)
            self._active_notes[midi_value] = note
        
    def on_note_off(self, midi_value: int):
        """ Remove note from _active_notes. """
        with self._lock:
            note = self._active_notes.pop(midi_value, None)
            if note is not None:
                note.set_off_time(self.now())


    # -------------------------------------------------------------------------
    # Consumer Methods
    # -------------------------------------------------------------------------

    def get_active_notes(self) -> list[Note]:
        """ Return a copy of a list of _active_notes' values. """
        with self._lock:
            return list(self._active_notes.values())
        
    def get_all_notes(self) -> list[Note]:
        """ Return a copy of _notes. """
        with self._lock:
            return list(self._notes)
        
    def get_recent_notes(self, window_sec: float) -> list[Note]:
        """ 
        Return a copy of a list of notes played from (window_sec) before to
        now. 
        """
        with self._lock:
            cutoff = self.now() - window_sec
            return [
                n for n in self._notes if n.is_active 
                or (n.off_time is not None and n.off_time >= cutoff)
            ]
        

    # -------------------------------------------------------------------------
    # Special Methods
    # -------------------------------------------------------------------------
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._notes)