import jack
from queue import Queue
from enum import Enum

class Message(Enum):
    START = 250
    STOP = 252

class Control:
    def __init__(self, port):
        self.midi_port = port
        self.toBeSent = Queue()
        self.playing = False

    def process(self):
        self.midi_port.clear_buffer()
        while not self.toBeSent.empty():
            self.midi_port.write_midi_event(0, [self.toBeSent.get()])

    def togglePlay(self):
        if self.playing:
            self.toBeSent.put(Message.STOP.value)
        else:
            self.toBeSent.put(Message.START.value)
        self.playing = not self.playing

    def sendMessage(self, msg):
        self.toBeSent.put(msg.value)
