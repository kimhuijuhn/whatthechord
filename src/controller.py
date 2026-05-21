from .events import EventBuffer
from .midi_constants import STATUS_MASK, MidiStatus, ControlChange

class MidiInputHandler:
    """
    Translates raw MIDI messages into EventBuffer calls using rtmidi callback.
    """

    def __init__(self, buffer: EventBuffer):
        self.buffer = buffer
        self._dispatch = {
            MidiStatus.NOTE_ON: self._handle_note_on,
            MidiStatus.NOTE_OFF: self._handle_note_off,
            MidiStatus.CONTROL_CHANGE: self._handle_cc,
            MidiStatus.PITCH_BEND: self._handle_pitch_bend,
        }
    
    def __call__(self, event, _data=None):
        message, _deltatime = event

        # ignore system calls for now
        if len(message) < 2:
            return
        
        status = message[0] & STATUS_MASK
        handler = self._dispatch.get(status)
        if handler:
            handler(message)


    # -------------------------------------------------------------------------
    # Note ON/OFF
    # -------------------------------------------------------------------------

    def _handle_note_on(self, message):
        """ """
        if len(message) < 3:
            return
        pitch, velocity = message[1], message[2]
        if velocity > 0:
            self.buffer.on_note_on(pitch, velocity)
        else:   # note-on with velocity 0 means note-off
            self.buffer.on_note_off(pitch)

    def _handle_note_off(self, message):
        if len(message) < 3:
            return
        self.buffer.on_note_off(message[1])


    # -------------------------------------------------------------------------
    # Expressive messages
    # -------------------------------------------------------------------------

    def _handle_cc(self, message):
        # TODO: implement later 
        if len(message) < 3:
            return
        controller, value = message[1], message[2]
        if controller == 64:  # sustain pedal
            pass

    def _handle_pitch_bend(self, message):
        # TODO: implement later
        if len(message) < 3:
            return
        # LSB + MSB, 14-bit value
        bend = (message[2] << 7) | message[1]
