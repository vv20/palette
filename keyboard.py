import numpy as np
import jack
from threading import Lock

class Keyboard:
    def __init__(self, port):
        print("init keyboard...")
        self.midi_port = port 
        self.toBePlayed = []
        self.toBeStopped = []
        self.lock = Lock()

    def process(self):
        self.lock.acquire()
        for key in self.toBePlayed:
            self.midi_port.write_midi_event(0, (144, key, 1))
        for key in self.toBeStopped:
            self.midi_port.write_midi_event(0, (128, key, 1))
        self.toBePlayed = []
        self.toBeStopped = []
        self.lock.release()

    def playKey(self, midi_key):
        print("playing key " + str(midi_key) + "...")
        self.lock.acquire()
        self.toBePlayed.append(midi_key)
        self.lock.release()

    def stopKey(self, midi_key):
        print("stopping key " + str(midi_key) + "...")
        self.lock.acquire()
        self.toBeStopped.append(midi_key)
        self.lock.release()
