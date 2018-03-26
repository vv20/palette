import jack
import numpy

from instruments.keyboard import Keyboard
from instruments.sampler import Sampler
from instruments.drummachine import DrumMachine

class Backend:
    def __init__(self, client, metronome, entities):
        '''
        entities: list
        List of constructors to initialise the instruments.
        '''
        self.client = client

        self.entities = []
        for i in range(0, len(entities)):
            port = self.client.midi_outports.register("out" + str(i))
            self.entities.append(entities[i](port, self.client.samplerate))

        self.metronome = metronome

        # callbacks
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(self.process)

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def process(self, no_frames):
        self.metronome.process()
        for entity in self.entities:
            entity.process(no_frames)
