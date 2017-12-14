import jack
import numpy

import keyboard
import drumpad
import sampler
import effects
import looper

client = None
keyboard_midi = None
drumpad_out = None
sampler_out = None
effects_in = None
effects_out = None
looper_in = None
looper_out = None

def shutdown():
    client.deactivate()
    client.close()

def process(frames):
    keyboard.process(frames, keyboard_midi)
    drumpad.process(frames, drumpad_out.get_array())
    sampler.process(frames, sampler_out.get_array())
    effects.process(frames, effects_in.get_array(), effects_out.get_array())
    looper.process(frames, looper_in.get_array(), looper_out.get_array())

def init():
    # register client
    client = jack.Client("palette")
    
    # register in-ports
    effects_in = client.inports.register("effects_in")
    looper_in = client.inports.register("looper_in")

    # register out-ports
    keyboard_midi = client.midi_outports.register("keyboard_out")
    drumpad_out = client.outports.register("drumpad_out")
    sampler_out = client.outports.register("sampler_out")
    effects_out = client.outports.register("effects_out")
    looper_out = client.outports.register("looper_out")

    # initialise the instruments
    keyboard.init(client.samplerate)
    drumpad.init(client.samplerate)
    sampler.init(client.samplerate)
    effects.init(client.samplerate)
    looper.init(client.samplerate)

    # set callbacks
    client.set_shutdown_callback(shutdown)
    client.set_process_callback(process)

    # activate client
    client.activate()

