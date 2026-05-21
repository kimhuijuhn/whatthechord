import time
from rtmidi import midiutil
from src.events import EventBuffer
from src.controller import MidiInputHandler

def main():
    midiin, portname = midiutil.open_midiport(0)
    print(f"Current Port: {portname}")

    # Listen to incoming MIDI messages
    buffer = EventBuffer()
    handler = MidiInputHandler(buffer)
    midiin.set_callback(handler)

    # for display purposes
    try:
        while True:
            active = buffer.get_active_notes()
            print(f"\rActive: {active}".ljust(80), end="", flush=True)
            time.sleep(0.05)  # 20Hz display refresh is plenty
    except KeyboardInterrupt:
        print(f"\nSession ended. Total notes: {len(buffer)}")
        midiin.close_port()


if __name__ == "__main__":
    main()