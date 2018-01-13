import numpy as np
import jack
from queue import Queue

class Keyboard:
    def __init__(self, port):
        print("init keyboard...")
        self.midi_port = port 
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()

    def process(self):
        self.midi_port.clear_buffer()
        while not self.toBePlayed.empty():
            self.midi_port.write_midi_event(0, (144, self.toBePlayed.get(), 1))
        while not self.toBeStopped.empty():
            self.midi_port.write_midi_event(0, (128, self.toBeStopped.get(), 1))

    def playKey(self, midi_key):
        print("playing key " + str(midi_key) + "...")
        self.toBePlayed.put(midi_key)

    def stopKey(self, midi_key):
        print("stopping key " + str(midi_key) + "...")
        self.toBeStopped.put(midi_key)
