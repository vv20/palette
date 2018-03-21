import jack
import numpy

from instruments.keyboard import Keyboard
from instruments.sampler import Sampler
from instruments.drummachine import DrumMachine

class Backend:
    def __init__(self, entities):
        '''
        entities: list
        List of constructors to initialise the instruments.
        '''
        # jack client
        self.client = jack.Client("palette", no_start_server = True)
        
        self.entities = []
        for i in range(0, len(entities)):
            port = self.client.midi_outports.register("out" + str(i))
            self.entities.append(entities[i](port, self.client.samplerate))

        # callbacks
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(self.process)

        if self.client.transport_state is jack.STARTING or self.client.transport_state is jack.ROLLING:
            self.transport_on = True
        else:
            self.transport_on = False

        # let's go
        self.client.activate()

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def process(self, no_frames):
        for entity in self.entities:
            entity.process(no_frames)

    def toggle_transport(self):
        if self.transport_on:
            self.client.trasport_stop()
        else:
            self.client.transport_start()
