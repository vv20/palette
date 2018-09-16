from abc import ABC, abstractmethod
from enum import Enum

class LooperMode(Enum):
    NORMAL = 0,
    RECORD = 1,
    DELETE = 2,
    HALF = 3,
    DOUBLE = 4

class Instrument(ABC):
    def __init__(self, port, samplerate):
        self.midi_port = port
        self.samplerate = samplerate
        # looper stuff
        self.looper_mode = LooperMode.NORMAL
        self.looper_functions = {
                LooperMode.NORMAL: self.toggle_loop,
                LooperMode.DELETE: self.delete_loop,
                LooperMode.DOUBLE: self.double_loop,
                LooperMode.RECORD: self.record_loop,
                LooperMode.HALF: self.half_loop
                }

    @abstractmethod
    def process(self, no_frames):
        pass

    @abstractmethod
    def key_pressed(self, key):
        pass

    @abstractmethod
    def key_released(self, key):
        pass

    def set_looper_mode(self, mode):
        self.looper_mode = mode

    def toggle_loop(self, loop):
        pass

    def record_loop(self, loop):
        pass

    def delete_loop(self, loop):
        pass

    def half_loop(self, loop):
        pass

    def double_loop(self, loop):
        pass

    def loop(self, loop_number):
        self.looper_functions[self.looper_mode](loop_number)
