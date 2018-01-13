import jack
import numpy

from keyboard import Keyboard
from control import Control

class Backend:
    def __init__(self):
        # jack client
        self.client = jack.Client("palette", no_start_server = True)
        # midi ports
        self.keyboard_midi = self.client.midi_outports.register("keyboard_out")
        self.control_midi = self.client.midi_outports.register("control_out")
        # entities
        self.keyboard = Keyboard(self.keyboard_midi)
        self.control = Control(self.control_midi)
        # callbacks
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(self.process)
        # let's go
        self.client.activate()

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def process(self, no_frames):
        self.keyboard.process()
        self.control.process()
