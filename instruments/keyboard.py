import jack
from queue import Queue

from instruments.instrument import Instrument

PLAY_NOTE_EVENT = 144
STOP_NOTE_EVENT = 128
DEFAULT_VEL = 63

class Keyboard(Instrument):
    def __init__(self, port, samplerate):
        super().__init__(port, samplerate)
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()

    def process(self, no_frames):
        self.midi_port.clear_buffer()
        while not self.toBePlayed.empty():
            note = self.toBePlayed.get()
            # note 0 means all notes off
            if note == 0:
                self.midi_port.write_midi_event(0, (176, 123, 0))
            else:
                self.midi_port.write_midi_event(0, 
                        (PLAY_NOTE_EVENT, note, DEFAULT_VEL))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, 
                    (STOP_NOTE_EVENT, self.toBeStopped.get(), DEFAULT_VEL))

    def key_pressed(self, key):
        try:
            self.toBePlayed.put(keyboard_mappings[key])
        except KeyError:
            pass

    def key_released(self, key):
        try:
            self.toBeStopped.put(keyboard_mappings[key])
        except KeyError:
            pass

keyboard_mappings = {
        # C-z
        29: 36,
        # C#-s
        22: 37,
        # D-x
        27: 38,
        # D#-d
        7: 39,
        # E-c
        6: 40,
        # F-v
        25: 41,
        # F#-g
        10: 42,
        # G-b
        5: 43,
        # G#-h
        11: 44,
        # A-n
        17: 45,
        # A#-j
        13: 46,
        # B-m
        16: 47,
        # C-,
        54: 48,
        # C#-l
        15: 49,
        # D-.
        55: 50,
        # D#-;
        51: 51,
        # E-/
        56: 52,
        # upper keyboard
        # F-q
        20: 53,
        # F#-2
        31: 54,
        # G-w
        26: 55,
        # G#-3
        32: 56,
        # A-e
        8: 57,
        # A#-4
        33: 58,
        # B-r
        21: 59,
        # C-t
        23: 60,
        # C#-6
        35: 61,
        # D-y
        28: 62,
        # D#-7
        36: 63,
        # E-u
        24: 64,
        # F-i
        12: 65,
        # F#-9
        38: 66,
        # G-o
        18: 67,
        # G#-0
        39: 68,
        # A-p
        19: 69
}

