from enum import IntEnum

STATUS_MASK = 0xF0

class MidiStatus(IntEnum):
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0


class ControlChange(IntEnum):
    """Common CC numbers."""
    SUSTAIN_PEDAL = 64
    SOSTENUTO = 66
    SOFT_PEDAL = 67
    EXPRESSION = 11
    MODULATION = 1