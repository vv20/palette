from abc import ABC, abstractmethod

class Instrument(ABC):
    def __init__(self, port, samplerate):
        self.midi_port = port;

    @abstractmethod
    def process(self, no_frames):
        pass

    @abstractmethod
    def key_pressed(self, key):
        pass

    @abstractmethod
    def key_released(self, key):
        pass
