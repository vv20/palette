import jack
import numpy

from keyboard import Keyboard

class Backend:
    def __init__(self):
        self.client = jack.Client("palette", no_start_server = True)
        self.keyboard_midi = self.client.midi_outports.register("keyboard_out")
        self.keyboard = Keyboard(self.keyboard_midi)
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(self.process)
        self.client.activate()

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def process(self, no_frames):
        self.keyboard.process()
