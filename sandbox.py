import time
from rtmidi import midiutil
import utility_functions as uf


midiin, portname = midiutil.open_midiport(0)
print("Current Port: ", portname)
uf.get_current_on_notes(midiin)