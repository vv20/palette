import jack
from queue import Queue

class Sampler:
    def __init__(self, port):
        self.midi_port = port
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()

    def process(self):
        self.midi_port.clear_buffer()
        while not self.toBePlayed.empty():
            self.midi_port.write_midi_event(0, (144, self.toBePlayed.get(), 1))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, (128, self.toBeStopped.get(), 1))

    def pressButton(self, midi_key):
        self.toBePlayed.put(midi_key)

