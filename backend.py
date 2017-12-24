import jack
import numpy

import keyboard
import sampler
import looper

client = None
keyboard_midi = None
sampler_midi = None
looper_in = None
looper_out = None

def shutdown():
    client.deactivate()
    client.close()

def process(frames):
    keyboard.process()
    sampler.process(frames)
    looper.process(frames, looper_in.get_array(), looper_out.get_array())

def init():
    # register client
    client = jack.Client("palette", no_start_server=True)
    
    # register in-port
    looper_in = client.inports.register("looper_in")

    # register out-ports
    looper_out = client.outports.register("looper_out")

    # register midi ports
    keyboard_midi = client.midi_outports.register("keyboard_out")
    sampler_midi = client.midi_outports.register("sampler_out")

    # initialise the instruments
    keyboard.init(keyboard_midi)
    sampler.init(sampler_midi)
    looper.init(client.samplerate)

    # set callbacks
    client.set_shutdown_callback(shutdown)
    client.set_process_callback(process)

    # activate client
    client.activate()

