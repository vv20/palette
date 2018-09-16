import jack
from queue import Queue

from instruments.instrument import Instrument

PLAY_NOTE_EVENT = 144
STOP_NOTE_EVENT = 128
DEFAULT_VEL = 63
BASE_NOTE = 60
BEATS_PER_BAR=8

class Push(Instrument):

    def __init__(self, port, samplerate):
        super().__init__(port, samplerate)
        self.bpm = 30.0
        self.frames_since = 0
        self.frames_per_beat = 60 / self.bpm / BEATS_PER_BAR * samplerate
        self.frames_until = self.frames_per_beat
        self.active_samples = []
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()

    def process(self, no_frames):
        self.midi_port.clear_buffer()
        if self.frames_until >= no_frames:
            self.frames_since += no_frames
            self.frames_until -= no_frames
            return
        while not self.toBePlayed.empty():
            channel = self.toBePlayed.get()
            self.midi_port.write_midi_event(self.frames_until, 
                    (PLAY_NOTE_EVENT + channel, BASE_NOTE, DEFAULT_VEL))
        while not self.toBeStopped.empty():
            channel = self.toBeStopped.get()
            self.midi_port.write_midi_event(self.frames_until,
                    (STOP_NOTE_EVENT + channel, BASE_NOTE, DEFAULT_VEL))
        self.frames_since = int(no_frames - self.frames_until)
        self.frames_until = int(self.frames_per_beat - self.frames_since)

    def key_pressed(self, key):
        if key not in self.active_samples:
            self.toBePlayed.put(sample_mappings[key])
            self.active_samples.append(key)
        else:
            self.toBeStopped.put(sample_mappings[key])
            self.active_samples.remove(key)

    def key_released(self, key):
        pass

sample_mappings = {
        # first row
        30: 0,
        31: 1,
        32: 2,
        33: 3,
        # second row
        20: 4,
        26: 5,
        8: 6,
        21: 7,
        # third row
        4: 8,
        22: 9,
        7: 10,
        9: 11,
        # forth row
        29: 12,
        27: 13,
        6: 14,
        25: 15
}
