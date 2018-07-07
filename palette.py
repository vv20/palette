import jack

from backend import Backend
from interface import Interface, Entity
from metronome import Metronome
from instruments.keyboard import Keyboard
from instruments.sampler import Sampler
from instruments.drummachine import DrumMachine
from instruments.instrument import LooperMode

# main pad
pad = list(range(4, 40))
pad.append(54)
pad.append(55)
pad.append(56)
pad.append(51)

# looper pad
looper = list(range(89,98))
looper_mode_mappings = {
        84: LooperMode.DELETE,
        85: LooperMode.RECORD,
        86: LooperMode.HALF,
        87: LooperMode.DOUBLE
        }

# headboard with instrument selection
headboard = list(range(58, 70))

class Main:
    def __init__(self):
        # jack client
        self.client = jack.Client("palette", no_start_server = True)
        
        # interface
        entities = [Entity.KEYBOARD, Entity.SAMPLER, Entity.DRUM_MACHINE]
        self.display = Interface(entities)

        # metronome
        self.metronome = Metronome(self.display, self.client)

        # backend
        constructors = [Keyboard, Sampler, DrumMachine]
        self.be = Backend(self.client, self.metronome, constructors)

        # misc
        self.pressed_keys = []
        self.fifo = open("palette.pipe", mode = "rt")
        self.current_inst_number = 0

        # let's go
        self.client.activate()
        self.display.paint_pad(0)
        self.metronome.sync_transport()

    def key_released(self, key):
        if key in pad:
            self.be.entities[self.current_inst_number].key_released(key)
            self.display.paint_key_off(key)
        elif key in range(84, 88):
            self.be.entities[self.current_inst_number].normal_mode()

    def key_pressed(self, key):
        if key in pad:
            self.be.entities[self.current_inst_number].key_pressed(key)
            self.display.paint_key_on(key)
        elif key in looper:
            self.be.entities[self.current_inst_number].loop(key - 89)
        elif key in looper_mode_mappings:
            self.be.entities[self.current_inst_number].set_looper_mode(looper_mode_mappings[key])
            # numpad /
        elif key == 84:
            self.be.entities[self.current_inst_number].delete_mode()
            # numpad *
        elif key == 85:
            self.be.entities[self.current_inst_number].record_mode()
            # numpad -
        elif key == 86:
            self.be.entities[self.current_inst_number].half_mode()
            # numpad +
        elif key == 87:
            self.be.entities[self.current_inst_number].double_mode()
            # space
        elif key == 44:
            self.metronome.toggle_transport()
            # esc
        elif key == 41:
            self.fifo.close()
            self.display.shutdown()
            quit()
            # instrument selection
        elif key in headboard:
            if key - 58 < len(self.be.entities):
                self.current_inst_number = key - 58
                self.display.paint_pad(self.current_inst_number)
            # left arrow, decrement bpm
        elif key == 80:
            self.metronome.decrement_bpm()
            # right arrow, increment bpm
        elif key == 79:
            self.metronome.increment_bpm()

if __name__ == "__main__":
    palette = Main()
    while True:
        line = palette.fifo.readline()
        if line[0] == '+':
            palette.key_pressed(int(line[1:]))
        else:
            palette.key_released(int(line[1:]))
