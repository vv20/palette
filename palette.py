from builtins import open, quit
from enum import Enum
import getopt
import jack
import json
from queue import Queue
import sys
import threading
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


class Singleton:
    __INSTANCE__ = None
    __INITIALISED__ = False

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__INSTANCE__:
            cls.__INSTANCE__ = super(Singleton, cls).__new__(*args, **kwargs)
        return cls.__INSTANCE__


class Main:
    def __init__(self):
        self.fifo = open(FIFO_NAME, mode='rt')
        self.currentInstNumber = 0
        Metronome().syncTransport()

    def shutdown(self):
        self.fifo.close()
        quit()

    def keyReleased(self, key):
        currentInst = InstrumentRepository().instruments[self.currentInstNumber]
        if key in PAD:
            currentInst.keyReleased(key)
        elif key in LOOP_OPS:
            currentInst.normalMode()

    def keyPressed(self, key):
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


def driver():
    # set up the usb magic
    keyboard = usb.core.find(bDeviceClass=0)
    firstInt = keyboard[0][(0,0)].bInterfaceNumber

    for config in keyboard:
        for interface in config:
            if keyboard.is_kernel_driver_active(interface.bInterfaceNumber):
                keyboard.detach_kernel_driver(interface.bInterfaceNumber);
                print('detaching a kernel driver')

    keyboard.set_configuration()
    endpoint = keyboard[0][(0,0)][0]

    # open the fifo for writing
    fifo = open(FIFO_NAME, mode='w')

    attempts = 10
    data = None
    pressed_keys = []
    while attempts > 0:
        try:
            data = keyboard.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
            if data == None:
                continue
            # clean up the keys that have been released
            for key in pressed_keys:
                if key not in data:
                    pressed_keys.remove(key)
                    try:
                        print('-' + str(key), file=fifo, flush=True)
                    except BrokenPipeError:
                        continue
            # trigger the pressed keys
            for i in range(2, len(data)):
                if data[i] == 0:
                    continue
                if data[i] not in pressed_keys:
                    pressed_keys.append(data[i])
                    try:
                        print('+' + str(data[i]), file=fifo, flush=True)
                    except BrokenPipeError:
                        continue
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                attempts -= 1
                print('timeout')


class Metronome(Singleton):
    def __init__(self):
        if self.__INITIALISED__:
            return
        self.beat = 0
        self.beatNumerator = DEFAULT_BEAT_NUMERATOR
        self.beatDenominator = DEFAULT_BEAT_DENOMINATOR
        self.bpm = DEFAULT_BPM
        self.ticksPerBeat = DEFAULT_TICKS_PER_BEAT
        self.ticksUntilBeat = self.ticksPerBeat
        self.__INITIALISED__ = True

    @property
    def transportOn(self):
        return Backend().client.transport_state != jack.STOPPED

    def toggleTransport(self):
        return {
            True: Backend().client.transport_stop,
            False: Backend().client.transport_start,
        }[self.transportOn]()

    def process(self, noOfFrames):
        if not self.transportOn:
            return
        position = Backend().client.transport_query_struct()
        self.beatDenominator = position['beat_type']
        self.beatNumerator = position['beats_per_bar']
        self.bpm = position['beats_per_minute']
        self.beat = position['beat'] - 1
        self.ticksUntilBeat = position['ticks_per_beat'] - position['tick']

    def syncTransport(self):
        _, struct = Backend().client.transport_query_struct()
        struct.bar = 1
        struct.beat = self.beat + 1
        struct.beat_type = self.beatDenominator
        struct.beats_per_bar = self.beatNumerator
        struct.beats_per_minute = self.bpm
        struct.ticks_per_beat = self.ticksPerBeat
        struct.valid = 16
        self.client.transport_reposition_struct(struct)

    def decrementBpm(self):
        _, struct = self.client.transport_query_struct()
        struct.beats_per_minute -= 1
        self.client.transport_reposition_struct(struct)

    def incrementBpm(self):
        _, struct = self.client.transport_query_struct()
        struct.beats_per_minute += 1
        self.client.transport_reposition_struct(struct)


class LoopMode(Enum):
    NORMAL = 1
    RECORD = 2
    DELETE = 3
    HALF = 4
    DOUBLE = 5


class Loop:

    def __init__(self):
        self.events = []
        self.position = 0
        self.length = 0
        self.recording = False
        self.playing = False

    def process(self, noOfFrames, events):
        if self.recording:
            self.events.extend([(self.position+t, e) for t,e in events])
            self.length += noOfFrames
            self.position += noOfFrames
            return []
        if self.playing:
            frame1 = range(self.position, min(self.position + noOfFrames, self.length))
            frame2 = range(noOfFrames - len(frame1))
            toReturn = [(t-self.position,e) for t,e in self.events if t in frame1] + [(self.length-self.position+t,e) for t,e in self.events if t in frame2]
            self.position = self.position + noOfFrames % self.length
            return toReturn
        return []

    def startRecording(self):
        self.clear()
        self.recording = True
        self.playing = False

    def stopRecording(self):
        self.recording = False
        self.playing = True

    def startPlaying(self):
        self.playing = True
        self.recording = False
        self.position = 0

    def stopPlaying(self):
        self.playing = False

    def clear(self):
        self.events = []

    def double(self):
        self.length = self.length * 2

    def half(self):
        self.length = self.length // 2
        if self.position >= self.length:
            self.position = self.position % self.length


class InstrumentRepository(Singleton):
    
    def __init__(self):
        if self.__INITIALISED__:
            return
        with open(CONFIG_PATH, 'r') as configFile:
            config = json.load(configFile)
            self.instruments = [Instrument(**c) for c in config]
        self.__INITIALISED__ = True

    def process(self, noOfFrames):
        for instrument in self.instruments:
            instrument.process(noOfFrames)

    def setClient(self, client):
        for instrument in self.instruments:
            instrument.setPort(client.midi_outports.register(instrument.name))


class Instrument:

    def __init__(self,
                 name='',
                 mapping={},
                 snap=False,
                 sticky=False,
                 snapBeatsPerBeat=1,
                 loopBeatsPerBeat=1,
                 ):
        self.name = name
        self.mapping = mapping
        self.snap = snap
        self.sticky = sticky
        self.snapBeatsPerBeat = snapBeatsPerBeat
        self.loopBeatsPerBeat = loopBeatsPerBeat
        self.loopMode = LoopMode.NORMAL
        self.soundingKeys = []
        self.toBePlayed = Queue()
        self.toBeStopped = Queue()
        self.loops = [Loop() for _ in range(9)]

    def setPort(self, port):
        self.port = port

    def process(self, noOfFrames):
        self.port.clear_buffer()
        events = []
        ticksPerSnap = Metronome().ticksPerBeat // self.snapBeatsPerBeat
        offset = 0 if not self.snap else ticksPerSnap-Metronome().ticksUntilBeat
        if self.snap and offset > noOfFrames:
            return
        while not self.toBePlayed.empty():
            channel, note = self.toBePlayed.get()
            event = (PLAY_NOTE_EVENT+channel, note, DEFAULT_VEL)
            self.port.write_midi_event(offset, event)
            events.append(event)
        while not self.toBeStopped.empty():
            channel, note = self.toBeStopped.get()
            event = (STOP_NOTE_EVENT+channel, note, DEFAULT_VEL)
            self.port.write_midi_event(offset, event)
            events.append(event)
        for loop in self.loops:
            loopEvents = loop.process(noOfFrames, events)
            for t,e in loopEvents:
                self.port.write_midi_event(t,e)

    def keyPressed(self, key):
        channel, note = self.mapping.get(key, (0,0))
        if not self.sticky:
            self.toBePlayed.put((channel, note))
        if self.sticky and not key in self.soundingKeys:
            self.soundingKeys.append(key)
            self.toBePlayed.put((channel, note))
            return
        if self.sticky and key in self.soundingKeys:
            self.soundingKeys.remove(key)
            self.toBeStopped.put((channel, note))

    def keyReleased(self, key):
        if not self.sticky:
            channel, note = self.mapping.get(key, (0,0))
            self.toBeStopped.put((channel, note))

    def loop(self, loopNumber):
        {
                LoopMode.NORMAL : self.normalModeCall,
                LoopMode.RECORD : self.recordModeCall,
                LoopMode.DELETE : self.deleteModeCall,
                LoopMode.HALF : self.halfModeCall,
                LoopMode.DOUBLE : self.doubleModeCall,
        }[self.loopMode](loopNumber)

    def deleteMode(self):
        self.loopMode = LoopMode.DELETE

    def recordMode(self):
        self.loopMode = LoopMode.RECORD

    def halfMode(self):
        self.loopMode = LoopMode.HALF

    def doubleMode(self):
        self.loopMode = LoopMode.DOUBLE

    def normalMode(self):
        self.loopMode = LoopMode.NORMAL

    def deleteModeCall(self, loopNumber):
        if not self.loops[loopNumber].playing:
            self.loops[loopNumber].clear()

    def recordModeCall(self, loopNumber):
        if self.loops[loopNumber].playing:
            return
        if self.loops[loopNumber].recording:
            self.loops[loopNumber].stopRecording()
        else:
            self.loops[loopNumber].startRecording()

    def halfModeCall(self, loopNumber):
        self.loops[loopNumber].half()

    def doubleModeCall(self, loopNumber):
        self.loops[loopNumber].double()

    def normalModeCall(self, loopNumber):
        if self.loops[loopNumber].playing:
            self.loops[loopNumber].stopPlaying()
        else:
            self.loops[loopNumber].startPlaying()


class Backend(Singleton):
    def __init__(self):
        if self.__INITIALISED__:
            return
        self.client = jack.Client(CLIENT_NAME, no_start_server=True)
        InstrumentRepository().setClient(self.client)
        self.client.set_shutdown_callback(self.shutdown)
        self.client.set_process_callback(self.process)
        self.client.activate()
        self.__INITIALISED__ = True

    def shutdown(self):
        self.client.deactivate()
        self.client.close()

    def process(self, noOfFrames):
        Metronome().process(noOfFrames)
        InstrumentRepository().process(noOfFrames)


def main():
    opts, _ = getopt.getopt(sys.argv[1:], 't')
    testRun = False
    for opt, arg in opts:
        testRun = opt == '-t'
    if not testRun:
        threading.Thread(target=driver, daemon=True).start()
    main = Main()
    while not EXITING:
        line = main.fifo.readline()
        if line[0] == '+':
            main.keyPressed(int(line[1:]))
        else:
            main.keyReleased(int(line[1:]))


if __name__ == '__main__':
    main()
