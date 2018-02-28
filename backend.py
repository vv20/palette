import jack
import numpy

from keyboard import Keyboard
from control import Control
from drummachine import DrumMachine

class Backend:
    def __init__(self):
        # jack client
        self.client = jack.Client("palette", no_start_server = True)
        # midi ports
        self.keyboard_midi = self.client.midi_outports.register("keyboard_out")
        self.sampler_midi = self.client.midi_outports.register("sampler_out")
        self.control_midi = self.client.midi_outports.register("control_out")
        self.drum_machine_midi = self.client.midi_outports.register("drum_machine_out")
        # entities
        self.keyboard = Keyboard(self.keyboard_midi)
        self.sampler = Keyboard(self.sampler_midi)
        self.control = Control(self.control_midi)
        self.drum_machine = DrumMachine(self.control_midi, self.client.samplerate)
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
        self.sampler.process()
        self.control.process()
        self.drum_machine.process(no_frames)
