'''

Palette: open-source configurable JACK MIDI driver for USB keyboards.
Copyright (C) 2020 Victor Vasilyev

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from builtins import open
from enum import Enum
import getopt
import json
from queue import Queue
import sys
import threading
import jack
from usb import core as usb


PLAY_NOTE_EVENT = 144
STOP_NOTE_EVENT = 128
DEFAULT_VEL = 64
CLIENT_NAME = 'palette'
FIFO_NAME = 'palette.pipe'
DEFAULT_BEAT_NUMERATOR = 4
DEFAULT_BEAT_DENOMINATOR = 4
DEFAULT_BPM = 120
DEFAULT_TICKS_PER_BEAT = 1920
CONFIG_PATH = 'config.json'
EXITING = False


class KeyMap(Enum):
    '''
    Enum that maps keyboard keys to byte values used in the USB protocol.
    '''
    A = 4
    B = 5
    C = 6
    D = 7
    E = 8
    F = 9
    G = 10
    H = 11
    I = 12
    J = 13
    K = 14
    L = 15
    M = 16
    N = 17
    O = 18
    P = 19
    Q = 20
    R = 21
    S = 22
    T = 23
    U = 24
    V = 25
    W = 26
    X = 27
    Y = 28
    Z = 29
    NUM1 = 30
    NUM2 = 31
    NUM3 = 32
    NUM4 = 33
    NUM5 = 34
    NUM6 = 35
    NUM7 = 36
    NUM8 = 37
    NUM9 = 38
    NUM0 = 39
    STOP = 55
    COMMA = 54
    FWDSLASH = 56
    SEMICOLON = 51
    NUMDIV = 84
    NUMMUL = 85
    NUMSUB = 86
    NUMADD = 87
    SPACE = 44
    ESC = 41
    ARROWUP = 79
    ARROWDOWN = 80
    NUMPAD1 = 89
    NUMPAD2 = 90
    NUMPAD3 = 91
    NUMPAD4 = 92
    NUMPAD5 = 93
    NUMPAD6 = 94
    NUMPAD7 = 95
    NUMPAD8 = 96
    NUMPAD9 = 97
    NUMPAD0 = 98
    F1 = 58
    F2 = 59
    F3 = 60
    F4 = 61
    F5 = 62
    F6 = 63
    F7 = 64
    F8 = 65
    F9 = 66
    F10 = 67
    F11 = 68
    F12 = 69


PAD = set([
    KeyMap.A.value,
    KeyMap.B.value,
    KeyMap.C.value,
    KeyMap.D.value,
    KeyMap.E.value,
    KeyMap.F.value,
    KeyMap.G.value,
    KeyMap.H.value,
    KeyMap.I.value,
    KeyMap.J.value,
    KeyMap.K.value,
    KeyMap.L.value,
    KeyMap.M.value,
    KeyMap.N.value,
    KeyMap.O.value,
    KeyMap.P.value,
    KeyMap.Q.value,
    KeyMap.R.value,
    KeyMap.S.value,
    KeyMap.T.value,
    KeyMap.U.value,
    KeyMap.V.value,
    KeyMap.W.value,
    KeyMap.X.value,
    KeyMap.Y.value,
    KeyMap.Z.value,
    KeyMap.NUM0.value,
    KeyMap.NUM1.value,
    KeyMap.NUM2.value,
    KeyMap.NUM3.value,
    KeyMap.NUM4.value,
    KeyMap.NUM5.value,
    KeyMap.NUM6.value,
    KeyMap.NUM7.value,
    KeyMap.NUM8.value,
    KeyMap.NUM9.value,
    KeyMap.STOP.value,
    KeyMap.COMMA.value,
    KeyMap.FWDSLASH.value,
    KeyMap.SEMICOLON.value,
])

LOOP_PAD = set([
    KeyMap.NUMPAD1.value,
    KeyMap.NUMPAD2.value,
    KeyMap.NUMPAD3.value,
    KeyMap.NUMPAD4.value,
    KeyMap.NUMPAD5.value,
    KeyMap.NUMPAD6.value,
    KeyMap.NUMPAD7.value,
    KeyMap.NUMPAD8.value,
    KeyMap.NUMPAD9.value,
])

LOOP_OPS = set([
    KeyMap.NUMMUL.value,
    KeyMap.NUMDIV.value,
    KeyMap.NUMADD.value,
    KeyMap.NUMSUB.value,
])

LOOP_NUMBERS = {
    KeyMap.NUMPAD1.value: 0,
    KeyMap.NUMPAD2.value: 1,
    KeyMap.NUMPAD3.value: 2,
    KeyMap.NUMPAD4.value: 3,
    KeyMap.NUMPAD5.value: 4,
    KeyMap.NUMPAD6.value: 5,
    KeyMap.NUMPAD7.value: 6,
    KeyMap.NUMPAD8.value: 7,
    KeyMap.NUMPAD9.value: 8,
}

HEADBOARD = set([
    KeyMap.F1.value,
    KeyMap.F2.value,
    KeyMap.F3.value,
    KeyMap.F4.value,
    KeyMap.F5.value,
    KeyMap.F6.value,
    KeyMap.F7.value,
    KeyMap.F8.value,
    KeyMap.F9.value,
    KeyMap.F10.value,
    KeyMap.F11.value,
    KeyMap.F12.value,
])

INSTRUMENT_NUMBERS = {
    KeyMap.F1.value: 0,
    KeyMap.F2.value: 1,
    KeyMap.F3.value: 2,
    KeyMap.F4.value: 3,
    KeyMap.F5.value: 4,
    KeyMap.F6.value: 5,
    KeyMap.F7.value: 6,
    KeyMap.F8.value: 7,
    KeyMap.F9.value: 8,
    KeyMap.F10.value: 9,
    KeyMap.F11.value: 10,
    KeyMap.F12.value: 11,
}

called = set()


def callOnce(f):
    global called

    def inner(*args, **kwargs):
        if f not in called:
            f(*args, **kwargs)
            called.add(f)
    return inner


class Singleton:
    '''
    Abstract class that ensures there is only ever one instance of an
    inheriting class in an application. New calls to the constructor return
    the same instance.
    '''
    __INSTANCE__ = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__INSTANCE__:
            cls.__INSTANCE__ = super(Singleton, cls).__new__(*args, **kwargs)
        return cls.__INSTANCE__


class Main:
    '''
    Main class of the application that handles key pressed and released logic.
    '''
    def __init__(self):
        self.fifo = open(FIFO_NAME, mode='rt')
        self.currentInstNumber = 0
        Metronome().syncTransport()

    def shutdown(self):
        '''
        Main application shutdown callback.
        '''
        self.fifo.close()
        sys.exit()

    def keyReleased(self, key):
        '''
        Main application callback for a key being released.
        '''
        currentInst = InstrumentRepository().instruments[
            self.currentInstNumber]
        if key in PAD:
            currentInst.keyReleased(key)
        elif key in LOOP_OPS:
            currentInst.normalMode()

    def keyPressed(self, key):
        '''
        Main application callback for a key being pressed.
        '''
        currentInst = InstrumentRepository().instruments[self.currentInstNumber]

        def noop():
            pass
        if key in PAD:
            currentInst.keyPressed(key)
        elif key in LOOP_PAD:
            currentInst.loop(LOOP_NUMBERS[key])
        elif key in HEADBOARD:
            instNumber = INSTRUMENT_NUMBERS[key]
            if instNumber < len(InstrumentRepository().instruments):
                self.currentInstNumber = instNumber
        else:
            {
                KeyMap.NUMDIV: currentInst.deleteMode,
                KeyMap.NUMMUL: currentInst.recordMode,
                KeyMap.NUMSUB: currentInst.halfMode,
                KeyMap.NUMADD: currentInst.doubleMode,
                KeyMap.SPACE: Metronome().toggleTransport,
                KeyMap.ESC: self.shutdown,
                KeyMap.ARROWDOWN: Metronome().decrementBpm,
                KeyMap.ARROWUP: Metronome().incrementBpm,
            }.get(key, noop)()


class Driver:
    '''
    Class responsible for hijacking the keyboard USB connection and writing
    key on and off events to the FIFO file to be consumed by the main
    application thread. If initialised in test mode, will consume information
    from stdin instead.
    '''

    def __init__(self, testMode=False):
        if testMode:
            self.readInput = self.readStdin
        else:
            self.readInput = self.readUSB
            self.keyboard = usb.find(bDeviceClass=0)
            for config in self.keyboard:
                for interface in config:
                    inNo = interface.bInterfaceNumber
                    if self.keyboard.is_kernel_driver_active(inNo):
                        self.keyboard.detach_kernel_driver(inNo)
            self.keyboard.set_configuration()
            self.endpoint = self.keyboard[0][(0, 0)][0]
        self.outputDest = open(FIFO_NAME, mode='w')
        self.pressedKeys = []

    def readStdin(self):
        '''
        Read input from the standard input stream.
        '''
        return sys.stdin.read()

    def readUSB(self):
        '''
        Read input from the USB port.
        '''
        return self.keyboard.read(
            self.endpoint.bEndpointAddress,
            self.endpoint.wMaxPacketSize)

    def run(self):
        while not EXITING:
            data = self.readInput()
            [print('-' + key, file=self.outputDest, flush=True) for key
                in self.pressedKeys if key not in data]
            pressedKeys = [key for key in data[2:] if key != 0]
            self.pressedKeys.extend(pressedKeys)
            [print('+' + key, file=self.outputDest, flush=True) for key
                in pressedKeys]


class Metronome(Singleton):
    '''
    Singleton class responsible for interacting with the jack transport.
    '''
    @callOnce
    def __init__(self):
        self.beat = 0
        self.beatNumerator = DEFAULT_BEAT_NUMERATOR
        self.beatDenominator = DEFAULT_BEAT_DENOMINATOR
        self.bpm = DEFAULT_BPM
        self.ticksPerBeat = DEFAULT_TICKS_PER_BEAT
        self.ticksUntilBeat = self.ticksPerBeat

    @property
    def transportOn(self):
        '''
        Checks if the jack transport is rolling or not.
        '''
        return Backend().client.transport_state != jack.STOPPED

    def toggleTransport(self):
        '''
        Stop the jack transport if it's rolling, start it if it's not.
        '''
        return {
            True: Backend().client.transport_stop,
            False: Backend().client.transport_start,
        }[self.transportOn]()

    def process(self):
        '''
        Syncs status of the metronome with the status of jack transport, to
        be called as part of the jack process callback.
        '''
        if not self.transportOn:
            return
        _, position = Backend().client.transport_query_struct()
        self.beatDenominator = position.beat_type
        self.beatNumerator = position.beats_per_bar
        self.bpm = position.beats_per_minute
        self.beat = position.beat - 1
        self.ticksUntilBeat = position.ticks_per_beat - position.tick

    def syncTransport(self):
        '''
        A method that syncs transport status with the status of the metronome,
        to be called on startup.
        '''
        _, struct = Backend().client.transport_query_struct()
        struct.bar = 1
        struct.beat = self.beat + 1
        struct.beat_type = self.beatDenominator
        struct.beats_per_bar = self.beatNumerator
        struct.beats_per_minute = self.bpm
        struct.ticks_per_beat = self.ticksPerBeat
        struct.valid = 16
        Backend().client.transport_reposition_struct(struct)

    def decrementBpm(self):
        '''
        Decrease the BPM of jack transport by 1.
        '''
        _, struct = Backend().client.transport_query_struct()
        struct.beats_per_minute -= 1
        Backend().client.transport_reposition_struct(struct)
        self.bpm = struct.beats_per_minute

    def incrementBpm(self):
        '''
        Increase the BPM of jack transport by 1.
        '''
        _, struct = Backend().client.transport_query_struct()
        struct.beats_per_minute += 1
        Backend().client.transport_reposition_struct(struct)
        self.bpm = struct.beats_per_minute


class LoopMode(Enum):
    '''
    Type of interaction an instrument can have with its loops.
    '''
    NORMAL = 1
    RECORD = 2
    DELETE = 3
    HALF = 4
    DOUBLE = 5


class Loop:
    '''
    Recordable loop of an instrument, capable of recording and playing back
    midi events.
    '''

    def __init__(self):
        self.events = []
        self.position = 0
        self.length = 0
        self.recording = False
        self.playing = False
        self.offset = 0

    def process(self, noOfFrames, events):
        '''
        The throughput method of the loop, to be called as part of the jack
        callback. Will record events passing through if in recording mode and
        will add recorded events to the throughput if in playing mode.
        '''
        if self.recording:
            self.events.extend([(self.position + t, e) for t, e in events])
            self.length += noOfFrames
            self.position += noOfFrames
            return []
        if self.playing:
            frame1 = range(self.position, min(self.position + noOfFrames,
                                              self.length))
            frame2 = range(noOfFrames - len(frame1))
            toReturn = [(t - self.position, e) for t, e in self.events if t in frame1] +\
                [(self.length - self.position + t, e) for t, e in self.events if t in frame2]
            self.position = self.position + noOfFrames % self.length
            return toReturn
        return []

    def startRecording(self, offset):
        '''
        Start recording the events from the process throughput.
        '''
        self.clear()
        self.recording = True
        self.playing = False

    def stopRecording(self, offset):
        '''
        Stop recording the events from the process throughput.
        '''
        self.recording = False
        self.playing = True

    def startPlaying(self, offset):
        '''
        Start injecting the recorded events into the process throughput.
        '''
        self.playing = True
        self.recording = False
        self.position = 0

    def stopPlaying(self, offset):
        '''
        Stop adding the recorded events to the process throughput.
        '''
        self.playing = False

    def clear(self):
        '''
        Delete the recorded events.
        '''
        self.events = []
        self.position = 0
        self.length = 0

    def double(self):
        '''
        Double the loop play time.
        '''
        self.length = self.length * 2

    def half(self):
        '''
        Half the loop play time.
        '''
        self.length = self.length // 2
        if self.position >= self.length:
            self.position = self.position % self.length


class InstrumentRepository(Singleton):
    '''
    Singleton class to encapsulate configured instruments.
    '''

    @callOnce
    def __init__(self):
        with open(CONFIG_PATH, 'r') as configFile:
            config = json.load(configFile)
            self.instruments = [Instrument(**c) for c in config]

    def process(self, noOfFrames):
        '''
        Process callback, to be called during the jack process callback.
        Calls the process callback on underlying instruments.
        '''
        for instrument in self.instruments:
            instrument.process(noOfFrames)

    def setClient(self, client):
        '''
        Assign a port from the jack client to the underlying instruments.
        '''
        for instrument in self.instruments:
            instrument.setPort(client.midi_outports.register(instrument.name))


class Instrument:
    '''
    Class representing a single key configuration on the pad.
    '''

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.mapping = kwargs['mapping']
        self.snap = kwargs.get('snap', False)
        self.sticky = kwargs.get('sticky', False)
        self.snapBeatsPerBeat = kwargs.get('snapBeatsPerBeat', 1)
        self.loopBeatsPerBeat = kwargs.get('loopBeatsPerBeat', 1)
        self.loopMode = LoopMode.NORMAL
        self.soundingKeys = []
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()
        self.loops = [Loop() for _ in range(9)]
        self.port = None

    def setPort(self, port):
        '''
        Process callback to be called as part of the jack callback.
        '''
        self.port = port

    def process(self, noOfFrames):
        '''
        Process callback to be called as part of the jack callback.
        '''
        self.port.clear_buffer()
        events = []
        ticksPerSnap = Metronome().ticksPerBeat // self.snapBeatsPerBeat
        offset = 0 if not self.snap else ticksPerSnap - Metronome().ticksUntilBeat
        if self.snap and offset > noOfFrames:
            return
        while not self.toBePlayed.empty():
            channel, note = self.toBePlayed.get()
            event = (PLAY_NOTE_EVENT + channel, note, DEFAULT_VEL)
            self.port.write_midi_event(offset, event)
            events.append(event)
        while not self.toBeStopped.empty():
            channel, note = self.toBeStopped.get()
            event = (STOP_NOTE_EVENT + channel, note, DEFAULT_VEL)
            self.port.write_midi_event(offset, event)
            events.append(event)
        for loop in self.loops:
            loopEvents = loop.process(noOfFrames, events)
            for time, event in loopEvents:
                self.port.write_midi_event(time, event)

    def keyPressed(self, key):
        '''
        Callback for pressing a key on an instrument.
        '''
        channel, note = self.mapping.get(key, (0, 0))
        if not self.sticky:
            self.toBePlayed.put((channel, note))
        if self.sticky and key not in self.soundingKeys:
            self.soundingKeys.append(key)
            self.toBePlayed.put((channel, note))
            return
        if self.sticky and key in self.soundingKeys:
            self.soundingKeys.remove(key)
            self.toBeStopped.put((channel, note))

    def keyReleased(self, key):
        '''
        Callback for releasing a key on an instrument.
        '''
        if not self.sticky:
            channel, note = self.mapping.get(key, (0, 0))
            self.toBeStopped.put((channel, note))

    def loop(self, loopNumber):
        '''
        Invoke the loop call.
        '''
        {
            LoopMode.NORMAL: self.normalModeCall,
            LoopMode.RECORD: self.recordModeCall,
            LoopMode.DELETE: self.deleteModeCall,
            LoopMode.HALF: self.halfModeCall,
            LoopMode.DOUBLE: self.doubleModeCall,
        }[self.loopMode](loopNumber)

    def deleteMode(self):
        '''
        Set the loop mode to deleting.
        '''
        self.loopMode = LoopMode.DELETE

    def recordMode(self):
        '''
        Set the loop mode to recording.
        '''
        self.loopMode = LoopMode.RECORD

    def halfMode(self):
        '''
        Set the loop mode to halving.
        '''
        self.loopMode = LoopMode.HALF

    def doubleMode(self):
        '''
        Set the loop mode to doubling.
        '''
        self.loopMode = LoopMode.DOUBLE

    def normalMode(self):
        '''
        Loop call for loop normal mode.
        '''
        self.loopMode = LoopMode.NORMAL

    def deleteModeCall(self, loopNumber):
        '''
        Loop call for loop deleting mode.
        '''
        if self.loops[loopNumber].playing or self.loops[loopNumber].recording:
            return
        self.loops[loopNumber].clear()

    def recordModeCall(self, loopNumber):
        '''
        Loop call for loop recording mode.
        '''
        if self.loops[loopNumber].playing:
            return
        if self.loops[loopNumber].recording:
            self.loops[loopNumber].stopRecording()
        else:
            self.loops[loopNumber].startRecording()

    def halfModeCall(self, loopNumber):
        '''
        Loop call for loop halving mode.
        '''
        self.loops[loopNumber].half()

    def doubleModeCall(self, loopNumber):
        '''
        Loop call for loop doubling mode.
        '''
        self.loops[loopNumber].double()

    def normalModeCall(self, loopNumber):
        '''
        Loop call for normal mode.
        '''
        if self.loops[loopNumber].playing:
            self.loops[loopNumber].stopPlaying()
        else:
            self.loops[loopNumber].startPlaying()


class Backend(Singleton):
    '''
    Singleton class responsible for jack connection.
    '''
    @callOnce
    def __init__(self):
        self.client = jack.Client(CLIENT_NAME, no_start_server=True)
        InstrumentRepository().setClient(self.client)
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(process)
        self.client.activate()

    def shutdown(self):
        '''
        Main jack shutdown callback.
        '''
        self.client.deactivate()
        self.client.close()


def process(noOfFrames):
    '''
    Main jack process callback.
    '''
    Metronome().process()
    InstrumentRepository().process(noOfFrames)


def main():
    '''
    Main flow of the script.
    '''
    opts, _ = getopt.getopt(sys.argv[1:], 't')
    testMode = False
    for opt, _ in opts:
        testMode = opt == '-t'
    driver = Driver(testMode=testMode)
    threading.Thread(target=driver.run, daemon=True).start()
    mainObj = Main()
    while not EXITING:
        line = mainObj.fifo.readline()
        if line[0] == '+':
            mainObj.keyPressed(int(line[1:]))
        else:
            mainObj.keyReleased(int(line[1:]))


if __name__ == '__main__':
    main()
