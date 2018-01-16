from control import Message
from backend import Backend
from keyboard import keyboard_mappings
from sampler import sampler_mappings
from interface import Interface

# main pad
pad = list(range(4, 40))
pad.append(54)
pad.append(55)
pad.append(56)
pad.append(51)

class Mode(Enum):
    KEYBOARD = 1
    SAMPLER = 2

class Main:
    def __init__(self):
        self.pressed_keys = []
        self.be = Backend()
        self.fifo = open("palette.pipe", mode = "rt")
        self.display = Interface()
        self.mode = Mode.KEYBOARD

    def key_released(self, key):
        if key in pad:
            if self.mode == Mode.KEYBOARD:
                try:
                    self.be.keyboard.stopKey(keyboard_mappings[key])
                    self.display.paint_key_off(key)
                except KeyError:
                    pass
            elif self.mode == Mode.SAMPLER:
                self.be.sampler.stopKey(sampler_mappings[key])

    def key_pressed(self, key):
        if key in pad:
            if self.mode == Mode.KEYBOARD:
                try:
                    self.be.keyboard.playKey(keyboard_mappings[key])
                    self.display.paint_key_on(key)
                except KeyError:
                    pass
            elif self.mode == Mode.SAMPLER:
                self.be.sampler.playKey(sampler_mappings[key])
            # space
        elif key == 44:
            self.be.control.sendMessage(Message.START)
            # esc
        elif key == 41:
            self.fifo.close()
            self.display.shutdown()
            quit()

if __name__ == "__main__":
    palette = Main()
    while True:
        line = palette.fifo.readline()
        if line[0] == '+':
            palette.key_pressed(int(line[1:]))
        else:
            palette.key_released(int(line[1:]))
