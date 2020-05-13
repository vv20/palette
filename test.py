'''

Unit test suite for Palette.
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
import random
import threading
import unittest
import mock
import palette


def patchHandler(testCase, patchName):
    '''
    Utility function for patching a member of the main application script.
    '''
    patcher = mock.patch('palette.{0}'.format(patchName))
    testCase.addCleanup(patcher.stop)
    return patcher.start()


class CallOnceTests(unittest.TestCase):
    '''
    Test set for the callOnce decorator that ensures functions are only
    called once.
    '''

    def setUp(self):
        self.counter = 0

    @palette.callOnce
    def func(self):
        self.counter += 1

    def testFuncShouldOnlyRunOnce(self):
        self.func()
        self.func()
        self.assertEqual(self.counter, 1)


class SingletonTests(unittest.TestCase):
    '''
    Test set for the abstract class that ensures all subclasses only have
    one instance at a time.
    '''

    class TestSingleton(palette.Singleton):
        '''
        Singleton class for testing.
        '''
        indicator = mock.MagicMock()

        @palette.callOnce
        def __init__(self):
            self.indicator.indicate()

    def setUp(self):
        self.TestSingleton.indicator.reset_mock()
        self.TestSingleton.__INSTANCE__ = None
        palette.called = set()

    def testInitShouldAlwaysReturnSameInstance(self):
        '''
        Test that the singleton constructor should always return the same
        instance.
        '''
        self.assertEqual(self.TestSingleton(), self.TestSingleton())

    def testInitShouldNotReturnNone(self):
        '''
        Test that the singleton constructor should not return None.
        '''
        self.assertIsNotNone(self.TestSingleton())

    def testInitShouldNotBeCalledMoreThanOnce(self):
        '''
        Test that the singleton __init__ method should not be called more than
        once.
        '''
        self.TestSingleton()
        self.TestSingleton()
        self.TestSingleton.indicator.indicate.assert_called_once()


class MainTests(unittest.TestCase):
    '''
    Test set for the main application class.
    '''

    def setUp(self):
        self.mockOpen = patchHandler(self, 'open')
        self.mockMetronome = patchHandler(self, 'Metronome')
        self.mockSys = patchHandler(self, 'sys')
        self.noOfInst = 5
        self.instruments = [mock.MagicMock() for _ in range(self.noOfInst)]
        self.mockInstRepo = patchHandler(self, 'InstrumentRepository')
        self.mockInstRepo().instruments = self.instruments
        self.main = palette.Main()

    def testInitShouldOpenFIFOFile(self):
        '''
        Test that the main application constructor opens the FIFO file for
        reading.
        '''
        self.mockOpen.assert_called_once_with(palette.FIFO_NAME, mode='rt')

    def testInitShouldSyncTransportWithMetronome(self):
        '''
        Test that the main application constructor syncs with jack transport
        through the metronome.
        '''
        self.mockMetronome().syncTransport.assert_called_once()

    def testKeyPressedShouldCallKeyPressedOnFirstInstrument(self):
        '''
        Test that the keyPressed callback, when called with a key in the main
        pad, calls the keyPressed callback on the current instrument with that
        key.
        '''
        key = random.sample(palette.PAD, 1)[0]
        self.main.keyPressed(key)
        self.instruments[0].keyPressed.assert_called_once_with(key)

    def testKeyPressedShouldCallLoopOnFirstInstrument(self):
        '''
        Test that the keyPressed callback, when called with a key in the loop
        pad, calls the loop callback on the active instrument with the number
        of that loop.
        '''
        for key in palette.LOOP_PAD:
            self.main.keyPressed(key)
            self.instruments[0].loop(key)
            self.fail()

    def testKeyPressedShouldSelectInstrument(self):
        '''
        Test that the keyPressed callback, when called with a headboard key,
        selects the instrument that that key represents as active.
        '''
        for i in range(self.noOfInst):
            instKey = i + palette.KeyMap.F1.value
            padKey = random.sample(palette.PAD, 1)[0]
            self.main.keyPressed(instKey)
            self.main.keyPressed(padKey)
            self.instruments[i].keyPressed.assert_called_once_with(padKey)

    def testKeyPressedShouldNotSelectInstrumentIfOutOfRange(self):
        '''
        Test that the keyPressed callback, when called with a headboard key,
        should not change the current instrument if the key does not represent
        a configured instrument.
        '''
        instKey = self.noOfInst + palette.KeyMap.F1.value
        padKey = random.sample(palette.PAD, 1)[0]
        self.main.keyPressed(instKey)
        self.main.keyPressed(padKey)
        self.instruments[0].keyPressed.assert_called_once_with(padKey)

    def testKeyPressedShouldCallDeleteModeOnCurrentInstrument(self):
        '''
        Test that the keyPressed callback, when called with the numpad slash
        key, sets the loop callback of the current instrument to deleting
        mode.
        '''
        self.main.keyPressed(palette.KeyMap.NUMDIV)
        self.instruments[0].deleteMode.assert_called_once()

    def testKeyPressedShouldCallRecordModeOnCurrentInstrument(self):
        '''
        Test that the keyPressed callback, when called with the numpad star
        key, sets the loop callback of the current instrument to recording
        mode.
        '''
        self.main.keyPressed(palette.KeyMap.NUMMUL)
        self.instruments[0].recordMode.assert_called_once()

    def testKeyPressedShouldCallHalfModeOnCurrentInstrument(self):
        '''
        Test that the keyPressed callback, when called with the numpad minus
        key, sets the loop callback of the current instrument to halving mode.
        '''
        self.main.keyPressed(palette.KeyMap.NUMSUB)
        self.instruments[0].halfMode.assert_called_once()

    def testKeyPressedShouldCallDoubleModeOnCurrentInstrument(self):
        '''
        Test that the keyPressed callback, when called with the numpad plus key,
        sets the loop callback of the current instrument to doubling mode.
        '''
        self.main.keyPressed(palette.KeyMap.NUMADD)
        self.instruments[0].doubleMode.assert_called_once()

    def testKeyPressedShouldCallToggleTransportOnMetronome(self):
        '''
        Test that the keyPressed callback, when called with the space key,
        toggles the jack transport through the metronome.
        '''
        self.main.keyPressed(palette.KeyMap.SPACE)
        self.mockMetronome().toggleTransport.assert_called_once()

    def testKeyPressedShouldCloseFIFOFileAndCallQuit(self):
        '''
        Test that the keyPressed callback, when called with the escape key,
        closes the FIFO file and shuts the application down.
        '''
        self.main.keyPressed(palette.KeyMap.ESC)
        self.mockOpen().close.assert_called_once()
        self.mockSys.exit.assert_called_once()

    def testKeyPressedShouldCallDecrementBPMOnMetronome(self):
        '''
        Test that the keyPressed callback, when called with the arrow down key,
        decrements the BPM through the metronome.
        '''
        self.main.keyPressed(palette.KeyMap.ARROWDOWN)
        self.mockMetronome().decrementBpm.assert_called_once()

    def testKeyPressedShouldCallIncrementBPMOnMetronome(self):
        '''
        Test that the keyPressed callback, when called with the arrow up key,
        calls increment the BPM through the metronome.
        '''
        self.main.keyPressed(palette.KeyMap.ARROWUP)
        self.mockMetronome().incrementBpm.assert_called_once()

    def testKeyPressedShouldNotThrowExceptionIfKeyNotRecognised(self):
        '''
        Test that the keyPressed callback, when called with a key that is not
        in the key map, does not throw an exception.
        '''
        invalidKey = 0
        self.assertNotIn(invalidKey, palette.KeyMap.__members__.values())
        self.main.keyPressed(invalidKey)

    def testKeyReleasedShouldCallKeyReleasedOnCurrentInstrument(self):
        '''
        Test that the keyReleased callback, when called with one of the keys in
        the main pad, calls the keyReleased callback on the current
        instrument.
        '''
        key = random.sample(palette.PAD, 1)[0]
        self.main.keyReleased(key)
        self.instruments[0].keyReleased.assert_called_once_with(key)

    def testKeyReleasedShouldCallNormalModeOnCurrentInstrument(self):
        '''
        Test the the keyReleased callback, when called with a key responsible
        for one of the loop modes, sets the loop callback of the
        current instrument to normal mode.
        '''
        key = random.sample(palette.LOOP_OPS, 1)[0]
        self.main.keyReleased(key)
        self.instruments[0].normalMode.assert_called_once_with()


class MetronomeTests(unittest.TestCase):
    '''
    Test set for the singleton class responsible for interacting with the jack
    transport.
    '''

    def setUp(self):
        palette.Metronome.__INSTANCE__ = None
        self.mockBackend = patchHandler(self, 'Backend')
        self.mockJack = patchHandler(self, 'jack')
        self.beatType = 4
        self.beatsPerBar = 3
        self.beatsPerMinute = 123
        self.beat = 1
        self.tick = 5
        self.ticksPerBeat = 1921
        self.transportStruct = mock.MagicMock()
        self.transportStruct.beat_type = self.beatType
        self.transportStruct.beats_per_bar = self.beatsPerBar
        self.transportStruct.beats_per_minute = self.beatsPerMinute
        self.transportStruct.beat = self.beat
        self.transportStruct.tick = self.tick
        self.transportStruct.ticks_per_beat = self.ticksPerBeat
        self.mockBackend().client.transport_query_struct.return_value = \
                (None, self.transportStruct)
        self.noOfFrames = 10

    def testInitShouldAlwaysReturnSameInstance(self):
        '''
        Test that the metronome constructor always returns the same instrance
        of the Metronome class.
        '''
        self.assertIsNotNone(palette.Metronome())
        self.assertEqual(palette.Metronome(), palette.Metronome())

    def testTransportOnShouldReturnFalseIfTransportIsStopped(self):
        '''
        Test that transportOn returns false if the state of jack transport is
        "stopped".
        '''
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        self.assertFalse(palette.Metronome().transportOn)

    def testTransportOnShouldReturnTrueIfTransportNotStopped(self):
        '''
        Test that transportOn returns true if the state of jack transport is
        "rolling".
        '''
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        self.assertTrue(palette.Metronome().transportOn)

    def testToggleTransportShouldStopTransportIfTransportOn(self):
        '''
        Test that toggling the transport stops the transport if it's rolling.
        '''
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        palette.Metronome().toggleTransport()
        self.mockBackend().client.transport_stop.assert_called_once()

    def testToggleTransportShouldStartTransportIfTransportOff(self):
        '''
        Test that toggling the transport starts the transport if it's stopped.
        '''
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        palette.Metronome().toggleTransport()
        self.mockBackend().client.transport_start.assert_called_once()

    def testProcessShouldNotQueryTransportIfTransportOff(self):
        '''
        Test that the metronome process callback does not query jack transport
        if the transport is stopped.
        '''
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        palette.Metronome().process()
        self.mockBackend().client.transport_query_struct.assert_not_called()

    def testProcessShouldAssignAttributesFromPositionStruct(self):
        '''
        Test that the metronome process callback does save the state of the
        jack transport to the metronome.
        '''
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        palette.Metronome().process()
        self.mockBackend().client.transport_query_struct.assert_called_once()
        self.assertEqual(palette.Metronome().beatNumerator, self.beatsPerBar)
        self.assertEqual(palette.Metronome().beatDenominator, self.beatType)
        self.assertEqual(palette.Metronome().bpm, self.beatsPerMinute)
        self.assertEqual(palette.Metronome().beat, self.beat - 1)
        self.assertEqual(palette.Metronome().ticksUntilBeat,
                         self.ticksPerBeat - self.tick)

    def testDecrementBPMShouldQueryJackTransport(self):
        self.fail()

    def testDecrementBPMShouldDecreaseBPMBy1(self):
        self.fail()

    def testDecrementBPMShouldSaveBPMToMetronome(self):
        self.fail()

    def testIncrementBPMShouldQueryJackTransport(self):
        self.fail()

    def testIncrementBPMShouldIncreaseBPMBy1(self):
        self.fail()

    def testIncrementBPMShouldSaveBPMToMetronome(self):
        self.fail()


class LoopTests(unittest.TestCase):
    '''
    Test set for the Loop class, responsible for recording and playing back
    MIDI events produced by an instrument.
    '''

    def setUp(self):
        self.loop = palette.Loop()
        self.event1 = 'mocKEvent1'
        self.event2 = 'mocKEvent2'
        self.event3 = 'mocKEvent3'
        self.time1 = 2
        self.time2 = 4
        self.time3 = 6
        self.events = [(self.time1, self.event1),
                       (self.time2, self.event2),
                       (self.time3, self.event3)]
        self.noOfFrames = 10

    def testProcessShouldPlayRecordedEventsAfterStopRecordingCalled(self):
        '''
        Test that the loop process callback automatically starts playing the
        recorded events back after recording.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        events = self.loop.process(self.noOfFrames, [])
        self.assertEqual(events, self.events)

    def testProcessShouldReturnEmptyListIfNoEventsRecorded(self):
        '''
        Test that the loop process callback does not play back any events if
        none have been recorded yet.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.stopRecording()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def testProcessShouldReturnEmptyListIfNoEventsInFrame(self):
        '''
        Test that the loop process callback does not playback any events if
        no events are to be played back as part of the current frame.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def testProcessShouldRollOverToStartIfFrameLongerThanRemainder(self):
        '''
        Test that the loop process callback starts playing the loop from the
        beginning seamlessly when it reaches the end of the loop in the middle
        of a frame.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        expectedEvents = [(t+self.noOfFrames, e) for t, e in self.events]
        actualEvents = self.loop.process(self.noOfFrames*2, [])
        self.assertEqual(actualEvents, expectedEvents)

    def testProcessShouldReturnEmptyListIfPlayingStartedThenStopped(self):
        '''
        Test that the loop process callback stops playing back recorded
        events when the loop is stopped.
        '''
        self.loop.startPlaying()
        self.loop.stopPlaying()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def testProcessShouldReturnEmptyListIfEventsRecordedThenCleared(self):
        '''
        Test that the loop process callback doesn't return any events after the
        loop has been cleared.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.stopPlaying()
        self.loop.clear()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def testProcessShouldAddEmptyTimeBetweenIterationsIfDoubleIsCalled(self):
        '''
        Test that, when a loop is doubled, the loop adds empty time equal
        to its previous length between iterations of itself.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.double()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])
        self.assertEqual(self.loop.process(self.noOfFrames, []), self.events)

    def testProcessShouldReturnEventsInFirstHalfIfHalfIsCalled(self):
        '''
        Test that, when a loop is halved, the process callback only
        returns the events in the first half of the loop.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.half()
        expectedEvents = [(t, e) for t, e in \
                self.events if t < self.noOfFrames/2]
        expectedEvents += [(t+self.noOfFrames//2, e) for t, e in \
                self.events if t < self.noOfFrames/2]
        self.assertEqual(self.loop.process(self.noOfFrames, []), expectedEvents)

    def testProcessShouldReturnAllEventsIfHalfThenDoubleAreCalled(self):
        '''
        Test that, when a loop is halved and then doubled again, the events in
        the second half are played again and not deleted.
        '''
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.half()
        self.loop.double()
        self.assertEqual(self.loop.process(self.noOfFrames, []), self.events)


class InstrumentRepositoryTests(unittest.TestCase):
    '''
    Test set for the singleton class that manages the configured instruments.
    '''

    def setUp(self):
        palette.InstrumentRepository.__INSTANCE__ = None
        palette.called = set()
        self.mockOpen = patchHandler(self, 'open')
        self.mockJson = patchHandler(self, 'json')
        self.mockInstrument = patchHandler(self, 'Instrument')
        self.noOfFrames = 10
        self.client = mock.MagicMock()
        self.config1 = {
            'param1': 'value1'
        }
        self.config2 = {
            'param2': 'value2'
        }
        self.config3 = {
            'param3': 'value3'
        }
        self.instrument1 = mock.MagicMock()
        self.instrument2 = mock.MagicMock()
        self.instrument3 = mock.MagicMock()
        self.configs = [self.config1, self.config2, self.config3]
        self.instruments = [
            self.instrument1,
            self.instrument2,
            self.instrument3
        ]
        self.mockJson.load.return_value = self.configs
        self.mockInstrument.side_effect = self.instruments

    def testInitShouldAlwaysReturnSameInstance(self):
        '''
        Test that the repository constructor always returns the same instance
        of the InstrumentRepository class.
        '''
        self.assertIsNotNone(palette.InstrumentRepository())
        self.assertEqual(palette.InstrumentRepository(),
                         palette.InstrumentRepository())

    def testInitShouldOpenConfigFile(self):
        '''
        Test that the repository constructor opens the JSON config file for
        reading.
        '''
        palette.InstrumentRepository()
        self.mockOpen.assert_called_once_with(palette.CONFIG_PATH, 'r')

    def testInitShouldLoadJsonFromConfigFile(self):
        '''
        Test that the repository constructor loads the configuration from the
        JSON file.
        '''
        palette.InstrumentRepository()
        self.mockJson.load.assert_called_once_with(self.mockOpen().__enter__())

    def testInitShouldInitInstrumentForEveryConfigInJson(self):
        '''
        Test that the repository constructor creates one instrument per
        configuration in the JSON config file.
        '''
        palette.InstrumentRepository()
        for config in self.configs:
            self.mockInstrument.assert_any_call(**config)

    def testProcessShouldCallProcessOnEveryInstrument(self):
        '''
        Test that the process callback of the instrument repository calls the
        process callback on each underlying instrument.
        '''
        palette.InstrumentRepository().process(self.noOfFrames)
        for instrument in self.instruments:
            instrument.process.assert_called_once_with(self.noOfFrames)

    def testSetClientShouldCallSetPortOnEveryInstrument(self):
        '''
        Test that calling setClient creates a MIDI port for each instrument
        and assigns it to the instrument.
        '''
        palette.InstrumentRepository().setClient(self.client)
        for instrument in self.instruments:
            self.client.midi_outports.register.assert_any_call(instrument.name)
            instrument.setPort.assert_called_once_with(
                self.client.midi_outports.register())


class InstrumentTests(unittest.TestCase):
    '''
    Test set for the Instrument class.
    '''

    def setUp(self):
        self.loops = [mock.MagicMock() for _ in range(9)]
        self.loop = patchHandler(self, 'Loop')
        self.loop.side_effect = self.loops
        for loop in self.loops:
            loop.process.return_value = []
        self.metronome = patchHandler(self, 'Metronome')
        self.ticksPerBeat = 20
        self.metronome().ticksPerBeat = self.ticksPerBeat
        self.port = mock.MagicMock()
        self.name = 'mockName'
        self.noOfFrames = 20
        self.key1 = 'key1'
        self.note1 = 1
        self.channel1 = 2
        self.mapping = {
            self.key1 : (self.channel1, self.note1),
        }
        self.snapBeatsPerBeat = 4
        self.loopBeatPerBeat = 2

    def testInitShouldCreateLoops(self):
        '''
        Test that the instrument constructor initialises the loops.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        self.assertEqual(instrument.loops, self.loops)

    def testSetPortShouldSetPort(self):
        '''
        Test that calling setPort on an instrument saves the port.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        self.assertEqual(self.port, instrument.port)

    def testProcessShouldClearBuffer(self):
        '''
        Test that the process callback of an instrument clears the buffer
        of its MIDI port before processing.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        instrument.process(self.noOfFrames)
        self.port.clear_buffer.assert_called_once()

    def testProcessShouldPlayNonStickyNotes(self):
        '''
        Test that the process callback of an instrument not in sticky mode
        plays a note-on event when a key is pressed and a note-off event
        when it's released.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        instrument.keyPressed(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(
            0, (palette.PLAY_NOTE_EVENT + self.channel1, self.note1,
                palette.DEFAULT_VEL))
        self.port.reset_mock()
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(
            0, (palette.STOP_NOTE_EVENT + self.channel1, self.note1,
                palette.DEFAULT_VEL))

    def testProcessShouldPlayStickyNotes(self):
        '''
        Test that the process callback of an instrument in sticky mode
        only plays a note-on event the first time a key is pressed and only a
        note-off event the second time it's pressed.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=True)
        instrument.setPort(self.port)
        instrument.keyPressed(self.key1)
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(
            0, (palette.PLAY_NOTE_EVENT + self.channel1, self.note1,
                palette.DEFAULT_VEL))
        self.port.reset_mock()
        instrument.keyPressed(self.key1)
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(
            0, (palette.STOP_NOTE_EVENT + self.channel1, self.note1,
                palette.DEFAULT_VEL))

    def testProcessShouldCallProcessOnEachLoop(self):
        '''
        Test that the process callback of an instrument passes the events
        it produces to the process callback of each of its loops.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        instrument.keyPressed(self.key1)
        instrument.process(self.noOfFrames)
        event = (palette.PLAY_NOTE_EVENT+self.channel1,
                 self.note1, palette.DEFAULT_VEL)
        for loop in self.loops:
            loop.process.assert_called_once_with(self.noOfFrames, [event])

    def testProcessShouldQuantiseSnapNotesToGivenBeats(self):
        '''
        Test that the process callback of an instrument in snap mode does
        not play notes until the next beat.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=True,
                                        sticky=False,
                                        snapBeatsPerBeat=self.snapBeatsPerBeat)
        self.metronome().ticksUntilBeat = 1
        instrument.setPort(self.port)
        instrument.process(1)
        instrument.keyPressed(self.key1)
        instrument.process(self.noOfFrames)
        offset = self.ticksPerBeat // self.snapBeatsPerBeat - 1
        event = (palette.PLAY_NOTE_EVENT+self.channel1,
                 self.note1, palette.DEFAULT_VEL)
        self.port.write_midi_event.assert_called_once_with(offset, event)

    def testProcessShouldOutputEventsProducedByLoops(self):
        '''
        Test that the process callback of an instrument outputs the events
        played back by loops to the jack midi port.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        event = (palette.PLAY_NOTE_EVENT+self.channel1,
                 self.note1, palette.DEFAULT_VEL)
        self.loops[0].process.return_value = [(0, event)]
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(0, event)

    def testDeleteModeShouldCallClearOnTheGivenLoop(self):
        '''
        Test that the loop callback in deleting mode deletes the loop.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = False
        instrument.deleteMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].clear.assert_called_once()

    def testDeleteModeShouldNotCallClearIfTheLoopIsRecording(self):
        '''
        Test that the loop callback in deleting mode does not delete the
        loop if it's recording.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = True
        instrument.deleteMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].clear.assert_not_called()

    def testDeleteModeShouldNotCallClearIfTheLoopIsPlaying(self):
        '''
        Test that the loop callback in deleting mode does not delete the
        loop if it's playing.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = True
        instrument.deleteMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].clear.assert_not_called()

    def testRecordModeShouldCallStartRecordingIfLoopIsNotRecording(self):
        '''
        Test that the loop callback in recording mode starts recording
        the loop if it isn't recording yet.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = False
        instrument.recordMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].startRecording.assert_called_once()

    def testRecordModeShouldCallStopRecordingIfLoopIsRecording(self):
        '''
        Test that the loop callback in recording mode stops recording
        the loop if it's recording.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = True
        instrument.recordMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].stopRecording.assert_called_once()

    def testRecordModeShouldDoNothingIfLoopIsPlaying(self):
        '''
        Test that the loop callback in recording mode does not start recording
        if the loop is playing.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = True
        self.loops[loopNumber].recording = False
        instrument.recordMode()
        instrument.loop(loopNumber)
        self.assertEqual(len(self.loops[loopNumber].method_calls), 0)

    def testRecordModeShouldQuantiseStartRecordingToGivenBeats(self):
        '''
        Test that the loop callback in recording mode does not start
        recording until the next beat if the loop is not recording.
        '''
        self.fail()

    def testRecordModeShouldQuantiseStopRecordingToGivenBeats(self):
        '''
        Test that the loop callback in recording mode continues recording
        until the next beat if the loop is recording.
        '''
        self.fail()

    def testHalfModeShouldCallHalfOnGivenLoop(self):
        '''
        Test that the loop callback in halving mode halves the loop playtime.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = False
        instrument.halfMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].half.assert_called_once()

    def testDoubleModeShouldCallDoubleOnGivenLoop(self):
        '''
        Test that the loop callback in doubling mode doubles the loop playtime.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = False
        instrument.doubleMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].double.assert_called_once()

    def testNormalModeShouldCallPlayIfLoopIsNotPlaying(self):
        '''
        Test that the loop callback in normal mode starts the loop playbakck if
        it isn't playing.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        self.loops[loopNumber].recording = False
        instrument.normalMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].startPlaying.assert_called_once()

    def testNormalModeShouldCallStopIfLoopIsPlaying(self):
        '''
        Test that the loop callback in normal mode stops the loop playback if
        it's playing.
        '''
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = True
        self.loops[loopNumber].recording = False
        instrument.normalMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].stopPlaying.assert_called_once()

    def testNormalModeShouldQuantisePlayToGivenBeats(self):
        '''
        Test that, when a loop is started, it doesn't start until the next beat.
        '''
        self.fail()

    def testNormalModeShouldQuantiseStopToGivenBeats(self):
        '''
        Test that, when a loop is stopped, it keeps playing until the next beat.
        '''
        self.fail()


class BackendTests(unittest.TestCase):
    '''
    Test set for the jack backend component of the application.
    '''

    def setUp(self):
        palette.Backend.__INSTANCE__ = None
        palette.called = set()
        self.jack = patchHandler(self, 'jack')
        self.instRepo = patchHandler(self, 'InstrumentRepository')
        self.metronome = patchHandler(self, 'Metronome')
        self.backend = palette.Backend()
        self.noOfFrames = 10

    def testInitShouldAlwaysReturnSameInstance(self):
        '''
        Test that the backend constructor always returns the same instance of
        the Backend class.
        '''
        self.assertIsNotNone(self.backend)
        self.assertEqual(self.backend, palette.Backend())

    def testInitShouldInitJackClient(self):
        '''
        Test that the backend constuctor initialises the jack client.
        '''
        self.jack.Client.assert_called_once_with(palette.CLIENT_NAME,
                                                 no_start_server=True)

    def testInitShouldSetClientOnInstrumentRepository(self):
        '''
        Test that the backend constructor passes the jack client to the
        instrument repository.
        '''
        self.instRepo().setClient.assert_called_once_with(self.jack.Client())

    def testInitShouldSetShutdownCallback(self):
        '''
        Test that the backend constructor sets the jack shutdown callback.
        '''
        self.jack.Client().set_shutdown_callback.assert_called_once_with(
            self.backend.shutdown)

    def testInitShouldSetProcessCallback(self):
        '''
        Test that the backend constructor sets the jack process callback.
        '''
        self.jack.Client().set_process_callback.assert_called_once_with(
            palette.process)

    def testInitShouldActivateClient(self):
        '''
        Test that the backend constructor activates the jack client.
        '''
        self.jack.Client().activate.assert_called_once()

    def testShutdownShouldDeactivateClient(self):
        '''
        Test that the shutdown callback of the backend deactivates the jack
        client.
        '''
        self.backend.shutdown()
        self.jack.Client().deactivate.assert_called_once()

    def testShutdownShouldCloseClient(self):
        '''
        Test that the shutdown callback of the backend closes the jack client.
        '''
        self.backend.shutdown()
        self.jack.Client().close.assert_called_once()


class MainFunctionTests(unittest.TestCase):
    '''
    Test set for the main logic flow of the application.
    '''

    def setUp(self):
        palette.EXITING = False
        self.mockMain = patchHandler(self, 'Main')
        self.mockThreading = patchHandler(self, 'threading')
        self.mockSys = patchHandler(self, 'sys')
        self.mainThread = threading.Thread(target=palette.main, daemon=True)
        self.mockSys.argv = ['scriptName']

    def tearDown(self):
        palette.EXITING = True

    def testMainShouldStartDriverThreadIfTestOptionNotGiven(self):
        '''
        Test that the main function starts the driver thread if run
        without the test flag.
        '''
        self.mainThread.start()
        self.mockThreading.Thread.assert_called_once_with(
            target=palette.driver, daemon=True)
        self.mockThreading.Thread().start.assert_called_once()

    def testMainShouldNotStartDriverThreadIfTestOptionGiven(self):
        '''
        Test that the main function does not start the driver thread if run
        with the test flag.
        '''
        self.mockSys.argv.append('-t')
        self.mainThread.start()
        self.mockThreading.Thread.assert_not_called()

    def testMainShouldCallKeyPressedIfLineStartsWithPlus(self):
        '''
        Test that when the main function reads +<key> from the pipe, it calls
        the key pressed callback.
        '''
        key = 5
        self.mockMain().fifo.readline.return_value = '+{0}'.format(key)
        self.mainThread.start()
        self.mockMain().keyPressed.assert_called_with(key)

    def testMainShouldCallKeyReleasedIfLineStartWithMinus(self):
        '''
        Test that when the main function reads -<key> from the pipe, it calls
        the key released callback.
        '''
        key = 5
        self.mockMain().fifo.readline.return_value = '-{0}'.format(key)
        self.mainThread.start()
        self.mockMain().keyReleased.assert_called_with(key)


class DriverTests(unittest.TestCase):
    '''
    Test set for the driver function.
    '''

    def setUp(self):
        palette.EXITING = False
        self.mockUsb = patchHandler(self, 'usb')
        self.mockOpen = patchHandler(self, 'open')

    def tearDown(self):
        palette.EXITING = True

    def testInitShouldSearchUSBDeviceClass(self):
        self.fail()

    def testInitShouldDetachKernelDrivers(self):
        self.fail()

    def testInitShouldSetConfiguration(self):
        self.fail()

    def testInitShouldOpenFIFOFileForWriting(self):
        self.fail()

    def testRunInTestModeShouldReadStdin(self):
        self.fail()

    def testRunInNormalModeShouldReadUSB(self):
        self.fail()


class ProcessCallbackTests(unittest.TestCase):
    '''
    Test set for the jack process callback.
    '''

    def setUp(self):
        self.mockMetronome = patchHandler(self, 'Metronome')
        self.mockInstRepo = patchHandler(self, 'InstrumentRepository')
        self.noOfFrames = 10

    def testProcessShouldProcessMetronome(self):
        '''
        Test that the main process callback calls the process
        callback of the metronome.
        '''
        palette.process(self.noOfFrames)
        self.mockMetronome().process.assert_called_once_with()

    def testProcessShouldProcessInsturmentRepository(self):
        '''
        Test that the main process callback calls the process
        callback of the instrument repository.
        '''
        palette.process(self.noOfFrames)
        self.mockInstRepo().process.assert_called_once_with(self.noOfFrames)


def main():
    '''
    Create and run the test suite.
    '''
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(SingletonTests))
    suite.addTests(loader.loadTestsFromTestCase(MainTests))
    suite.addTests(loader.loadTestsFromTestCase(MetronomeTests))
    suite.addTests(loader.loadTestsFromTestCase(LoopTests))
    suite.addTests(loader.loadTestsFromTestCase(InstrumentRepositoryTests))
    suite.addTests(loader.loadTestsFromTestCase(InstrumentTests))
    suite.addTests(loader.loadTestsFromTestCase(BackendTests))
    suite.addTests(loader.loadTestsFromTestCase(MainFunctionTests))
    suite.addTests(loader.loadTestsFromTestCase(DriverTests))
    suite.addTests(loader.loadTestsFromTestCase(CallOnceTests))
    suite.addTests(loader.loadTestsFromTestCase(ProcessCallbackTests))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
