import numpy as np
import jack

toBePlayed = []
toBeStopped = []

midi_port = None

def init(port):
    midi_port = port

def process():
    for key in toBePlayed:
        port.write_midi_event(0, (144, key, 1))
    for key in toBeStopped:
        port.write_midi_event(0, (128, key, 1))
    pass

def playKey(midi_key):
    toBePlayed.append(midi_key)

def stopKey(midi_key):
    toBeStopped.append(midi_key)
