import numpy as np
import jack

toBePlayed = []
toBeStopped = []

def init():
    pass

def process(nFrames, port):
    pass

def playKey(midi_key):
    toBePlayed.append(midi_key)

def releaseKey(midi_key):
    toBeStopped.append(midi_key)
