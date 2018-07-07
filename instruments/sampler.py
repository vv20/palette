import jack
from queue import Queue

from instruments.instrument import Instrument

PLAY_NOTE_EVENT = 144
STOP_NOTE_EVENT = 128
DEFAULT_NOTE = 60
DEFAULT_VEL = 63

class Sampler(Instrument):

    def __init__(self, port, samplerate):
        super().__init__(port, samplerate)
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()
        self.current_note = DEFAULT_NOTE

    def process(self, no_frames):
        self.midi_port.clear_buffer()
        while not self.toBePlayed.empty():
            channel = self.toBePlayed.get()
            # note 0 means all notes off
            if channel == -1:
                self.midi_port.write_midi_event(0, (176, 123, 0))
            else:
                self.midi_port.write_midi_event(0, 
                        (PLAY_NOTE_EVENT + channel, self.current_note, DEFAULT_VEL))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, 
                    (STOP_NOTE_EVENT + self.toBeStopped.get(), self.current_note, DEFAULT_VEL))

    def key_pressed(self, key):
        if key in note_mappings:
            self.current_note = note_mappings[key]
        if key in channel_mappings:
            self.toBePlayed.put(channel_mappings[key])

    def key_released(self, key):
        if key in note_mappings:
            self.current_note = DEFAULT_NOTE
        if key in channel_mappings:
            self.toBeStopped.put(channel_mappings[key])

channel_mappings = {
        # first line
        30: 0,
        31: 1,
        32: 2,
        33: 3,
        # second line
        20: 4,
        26: 5,
        8: 6,
        21: 7,
        # third line
        4: 8,
        22: 9,
        7: 10,
        9: 11,
        # forth line
        29: 12,
        27: 13,
        6: 14,
        25: 15,
}

note_mappings = {
        36: DEFAULT_NOTE,
        37: DEFAULT_NOTE + 1,
        38: DEFAULT_NOTE + 2,
        39: DEFAULT_NOTE + 3,
        24: DEFAULT_NOTE + 4,
        12: DEFAULT_NOTE + 5,
        18: DEFAULT_NOTE + 6,
        19: DEFAULT_NOTE + 7,
        13: DEFAULT_NOTE + 8,
        14: DEFAULT_NOTE + 9,
        15: DEFAULT_NOTE + 10,
        51: DEFAULT_NOTE + 11,
        16: DEFAULT_NOTE + 12,
        54: DEFAULT_NOTE + 13,
        55: DEFAULT_NOTE + 14,
        56: DEFAULT_NOTE + 15,
}
