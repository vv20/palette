import jack
from queue import Queue

from instruments.instrument import Instrument

class Sampler(Instrument):

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
                self.midi_port.write_midi_event(0, (144, note, 1))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, (128, self.toBeStopped.get(), 1))

    def key_pressed(self, key):
        self.toBePlayed.put(sampler_mappings[key])

    def key_released(self, key):
        self.toBeStopped.put(sampler_mappings[key])

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
        25: 69,
        5: 70,
        17: 71,
        16: 72,
        54: 73,
        55: 74,
        56: 75
}
