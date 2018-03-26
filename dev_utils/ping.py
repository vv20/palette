import jack

class Pinger:
    def __init__(self):
        self.channel_no = 0
        self.note = 0
        self.counter = 0
        print("initialising client")
        self.client = jack.Client("ping", no_start_server=True)
        print("initialising port")
        self.port = self.client.midi_outports.register("out")
        print("registering process callback")
        self.client.set_process_callback(self.process)
        print("lets go")
        self.client.activate()

    def process(self, no_frames):
        self.counter = self.counter + 1
        if self.counter < 10:
            return
        self.counter = 0
        print("pinging channel " + str(self.channel_no) + " with note " + str(self.note))
        self.port.write_midi_event(0, (144 + self.channel_no, self.note, 127))
        self.note = self.note + 1
        if self.note > 127:
            self.note = 0
            self.channel_no = self.channel_no + 1
        if self.channel_no > 15:
            self.channel_no = 0

pinger = Pinger()
input()
