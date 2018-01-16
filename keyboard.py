import jack
from queue import Queue

class Keyboard:
    def __init__(self, port):
        self.midi_port = port 
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()

    def process(self):
        self.midi_port.clear_buffer()
        while not self.toBePlayed.empty():
            note = self.toBePlayed.get()
            # note 0 means all notes off
            if note == 0:
                self.midi_port.write_midi_event(0, (176, 123, 0))
            else:
                self.midi_port.write_midi_event(0, (144, self.toBePlayed.get(), 1))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, (128, self.toBeStopped.get(), 1))

    def playKey(self, midi_key):
        self.toBePlayed.put(midi_key)

    def stopKey(self, midi_key):
        self.toBeStopped.put(midi_key)

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

sampler_mappings = {
        30: 36,
        31: 37,
        32: 38,
        33: 39,
        34: 40,
        35: 41,
        36: 42,
        37: 43,
        38: 44,
        39: 45,
        20: 46,
        26: 47,
        8: 48,
        21: 49,
        23: 50,
        28: 51,
        24: 52,
        12: 53,
        18: 54,
        19: 55,
        4: 56,
        22: 57,
        7: 58,
        9: 59,
        10: 60,
        11: 61,
        13: 62,
        14: 63,
        15: 64,
        51: 65,
        29: 66,
        27: 67,
        6: 68,
        10: 69,
        5: 70,
        17: 71,
        16: 72,
        54: 73,
        55: 74,
        56: 75
}
