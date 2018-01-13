import jack
from queue import Queue
from enum import Enum

class Message(Enum):
    START = 250

class Control:
    def __init__(self, port):
        self.midi_port = port
        self.toBeSent = Queue()

    def process(self):
        self.midi_port.clear_buffer()
        while not self.toBeSent.empty():
            self.midi_port.write_midi_event(0, [self.toBeSent.get()])

    def sendMessage(self, msg):
        self.toBeSent.put(msg.value)
