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

# MIDI Key Signature meta message → major tonic (pitch class).
# Index: number of sharps (positive) or flats (negative), -7 to +7.
# Value: tonic pitch class (0-11) of the major key.
# Minor keys are derived as (major_tonic - 3) % 12 (relative minor).
KEY_SIGNATURE_TO_TONIC = {
    0: 0,    # C
    1: 7,    # G
    2: 2,    # D
    3: 9,    # A
    4: 4,    # E
    5: 11,   # B
    6: 6,    # F#
    7: 1,    # C#
    -1: 5,   # F
    -2: 10,  # Bb → A#
    -3: 3,   # Eb → D#
    -4: 8,   # Ab → G#
    -5: 1,   # Db → C# (enharmonic with 7 sharps)
    -6: 6,   # Gb → F# (enharmonic with 6 sharps)
    -7: 11,  # Cb → B  (enharmonic with 5 sharps)
}