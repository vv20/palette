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
import mock
import random
import palette
import threading
import unittest


def patchHandler(testCase, patchName):
    patcher = mock.patch('palette.{0}'.format(patchName))
    testCase.addCleanup(patcher.stop)
    return patcher.start()


class SingletonTests(unittest.TestCase):

    class TestSingleton(palette.Singleton):
        indicator = mock.MagicMock()
        def __init__(self):
            if self.__INITIALISED__:
                return
            self.indicator.indicate()
            self.__INITIALISED__ = True

    def setUp(self):
        self.TestSingleton.indicator.reset_mock()
        self.TestSingleton.__INSTANCE__ = None

    def test_init_shouldAlwaysReturnSameInstance(self):
        self.assertEqual(self.TestSingleton(), self.TestSingleton())

    def test_init_shouldNotReturnNull(self):
        self.assertIsNotNone(self.TestSingleton())

    def test_init_shouldNotBeCalledMoreThanOnce(self):
        self.TestSingleton()
        self.TestSingleton()
        self.TestSingleton.indicator.indicate.assert_called_once()


class MainTests(unittest.TestCase):

    def setUp(self):
        self.mockOpen = patchHandler(self, 'open')
        self.mockMetronome = patchHandler(self, 'Metronome')
        self.mockQuit = patchHandler(self, 'quit')
        self.noOfInst = 5
        self.instruments = [mock.MagicMock() for _ in range(self.noOfInst)]
        self.mockInstRepo = patchHandler(self, 'InstrumentRepository')
        self.mockInstRepo().instruments = self.instruments
        self.main = palette.Main()

    def test_init_shouldOpenFIFOFile(self):
        self.mockOpen.assert_called_once_with(palette.FIFO_NAME, mode='rt')

    def test_init_shouldSyncTransportWithMetronome(self):
        self.mockMetronome().syncTransport.assert_called_once()

    def test_keyPressed_shouldCallKeyPressedOnFirstInstrument(self):
        key = random.sample(palette.PAD, 1)[0]
        self.main.keyPressed(key)
        self.instruments[0].keyPressed.assert_called_once_with(key)

    def test_keyPressed_shouldCallLoopOnFirstInstrument(self):
        for key in palette.LOOP_PAD:
            self.main.keyPressed(key)
            self.instruments[0].loop(key)

    def test_keyPressed_shouldSelectInstrument(self):
        for i in range(self.noOfInst):
            instKey = i + palette.KeyMap.F1.value
            padKey = random.sample(palette.PAD, 1)[0]
            self.main.keyPressed(instKey)
            self.main.keyPressed(padKey)
            self.instruments[i].keyPressed.assert_called_once_with(padKey)

    def test_keyPressed_shouldNotSelectInstrumentIfOutOfRange(self):
        instKey = self.noOfInst + palette.KeyMap.F1.value
        padKey = random.sample(palette.PAD, 1)[0]
        self.main.keyPressed(instKey)
        self.main.keyPressed(padKey)
        self.instruments[0].keyPressed.assert_called_once_with(padKey)

    def test_keyPressed_shouldCallDeleteModeOnCurrentInstrument(self):
        self.main.keyPressed(palette.KeyMap.NUMDIV)
        self.instruments[0].deleteMode.assert_called_once()

    def test_keyPressed_shouldCallRecordModeOnCurrentInstrument(self):
        self.main.keyPressed(palette.KeyMap.NUMMUL)
        self.instruments[0].recordMode.assert_called_once()

    def test_keyPressed_shouldCallHalfModeOnCurrentInstrument(self):
        self.main.keyPressed(palette.KeyMap.NUMSUB)
        self.instruments[0].halfMode.assert_called_once()

    def test_keyPressed_shouldCallDoubleModeOnCurrentInstrument(self):
        self.main.keyPressed(palette.KeyMap.NUMADD)
        self.instruments[0].doubleMode.assert_called_once()

    def test_keyPressed_shouldCallToggleTransportOnMetronome(self):
        self.main.keyPressed(palette.KeyMap.SPACE)
        self.mockMetronome().toggleTransport.assert_called_once()

    def test_keyPressed_shouldCloseFIFOFileAndCallQuit(self):
        self.main.keyPressed(palette.KeyMap.ESC)
        self.mockOpen().close.assert_called_once()
        self.mockQuit.assert_called_once()

    def test_keyPressed_shouldCallDecrementBPMOnMetronome(self):
        self.main.keyPressed(palette.KeyMap.ARROWDOWN)
        self.mockMetronome().decrementBpm.assert_called_once()

    def test_keyPressed_shouldCallIncrementBPMOnMetronome(self):
        self.main.keyPressed(palette.KeyMap.ARROWUP)
        self.mockMetronome().incrementBpm.assert_called_once()

    def test_keyPressed_shouldNotThrowExceptionIfKeyNotRecognised(self):
        invalidKey = 0
        self.assertNotIn(invalidKey, palette.KeyMap.__members__.values())
        self.main.keyPressed(invalidKey)

    def test_keyReleased_shouldCallKeyReleasedOnCurrentInstrument(self):
        key = random.sample(palette.PAD, 1)[0]
        self.main.keyReleased(key)
        self.instruments[0].keyReleased.assert_called_once_with(key)

    def test_keyReleased_shouldCallNormalModeOnCurrentInstrument(self):
        key = random.sample(palette.LOOP_OPS, 1)[0]
        self.main.keyReleased(key)
        self.instruments[0].normalMode.assert_called_once_with()


class MetronomeTests(unittest.TestCase):

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
        self.transportStruct = {
                'beat_type' : self.beatType,
                'beats_per_bar': self.beatsPerBar,
                'beats_per_minute': self.beatsPerMinute,
                'beat': self.beat,
                'tick': self.tick,
                'ticks_per_beat': self.ticksPerBeat
        }
        self.mockBackend().client.transport_query_struct.return_value = \
                self.transportStruct
        self.noOfFrames = 10

    def test_init_shouldAlwaysReturnSameInstance(self):
        self.assertIsNotNone(palette.Metronome())
        self.assertEqual(palette.Metronome(), palette.Metronome())

    def test_transportOn_shouldReturnFalseIfTransportIsStopped(self):
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        self.assertFalse(palette.Metronome().transportOn)

    def test_transportOn_shouldReturnTrueIfTransportNotStopped(self):
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        self.assertTrue(palette.Metronome().transportOn)

    def test_toggleTransport_shouldStopTransportIfTransportOn(self):
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        palette.Metronome().toggleTransport()
        self.mockBackend().client.transport_stop.assert_called_once()

    def test_toggleTransport_shouldStartTransportIfTransportOff(self):
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        palette.Metronome().toggleTransport()
        self.mockBackend().client.transport_start.assert_called_once()

    def test_process_shouldNotQueryTransportIfTransportOff(self):
        self.mockBackend().client.transport_state = self.mockJack.STOPPED
        palette.Metronome().process(self.noOfFrames)
        self.mockBackend().client.transport_query_struct.assert_not_called()

    def test_process_shouldAssignAttributesFromPositionStruct(self):
        self.mockBackend().client.transport_state = self.mockJack.ROLLING
        palette.Metronome().process(self.noOfFrames)
        self.mockBackend().client.transport_query_struct.assert_called_once()
        self.assertEqual(palette.Metronome().beatNumerator, self.beatsPerBar)
        self.assertEqual(palette.Metronome().beatDenominator, self.beatType)
        self.assertEqual(palette.Metronome().bpm, self.beatsPerMinute)
        self.assertEqual(palette.Metronome().beat, self.beat - 1)
        self.assertEqual(palette.Metronome().ticksUntilBeat,
                self.ticksPerBeat - self.tick)


class LoopTests(unittest.TestCase):

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

    def test_process_shouldPlayRecordedEventsAfterStopRecordingCalled(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        events = self.loop.process(self.noOfFrames, [])
        self.assertEqual(events, self.events)

    def test_process_shouldReturnEmptyListIfNoEventsRecorded(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.stopRecording()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def test_process_shouldReturnEmptyListIfNoEventsInFrame(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def test_process_shouldRollOverToStartIfFrameLongerThanRemainder(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, [])
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        expectedEvents = [(t+self.noOfFrames, e) for t,e in self.events]
        actualEvents = self.loop.process(self.noOfFrames*2, [])
        self.assertEqual(actualEvents, expectedEvents)

    def test_process_shouldReturnEmptyListIfPlayingStartedThenStopped(self):
        self.loop.startPlaying()
        self.loop.stopPlaying()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def test_process_shouldReturnEmptyListIfEventsRecordedThenCleared(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.clear()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])

    def test_process_shouldAddEmptyTimeBetweenIterationsIfDoubleIsCalled(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.double()
        self.assertEqual(self.loop.process(self.noOfFrames, []), [])
        self.assertEqual(self.loop.process(self.noOfFrames, []), self.events)

    def test_process_shouldReturnEventsInFirstHalfIfHalfIsCalled(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.half()
        expectedEvents = [(t,e) for t,e in self.events if t<self.noOfFrames/2]
        expectedEvents += \
        [(t+self.noOfFrames//2,e) for t,e in self.events if t<self.noOfFrames/2]
        self.assertEqual(self.loop.process(self.noOfFrames, []), expectedEvents)

    def test_process_shouldReturnAllEventsIfHalfThenDoubleAreCalled(self):
        self.loop.startRecording()
        self.loop.process(self.noOfFrames, self.events)
        self.loop.stopRecording()
        self.loop.half()
        self.loop.double()
        self.assertEqual(self.loop.process(self.noOfFrames, []), self.events)


class InstrumentRepositoryTests(unittest.TestCase):

    def setUp(self):
        palette.InstrumentRepository.__INSTANCE__ = None
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

    def test_init_shouldAlwaysReturnSameInstance(self):
        self.assertIsNotNone(palette.InstrumentRepository())
        self.assertEqual(palette.InstrumentRepository(),
                palette.InstrumentRepository())

    def test_init_shouldOpenConfigFile(self):
        palette.InstrumentRepository()
        self.mockOpen.assert_called_once_with(palette.CONFIG_PATH, 'r')

    def test_init_shouldLoadJsonFromConfigFile(self):
        palette.InstrumentRepository()
        self.mockJson.load.assert_called_once_with(self.mockOpen().__enter__())

    def test_init_shouldInitInstrumentForEveryConfigInJson(self):
        palette.InstrumentRepository()
        for config in self.configs:
            self.mockInstrument.assert_any_call(**config)

    def test_process_shouldCallProcessOnEveryInstrument(self):
        palette.InstrumentRepository().process(self.noOfFrames)
        for instrument in self.instruments:
            instrument.process.assert_called_once_with(self.noOfFrames)

    def test_setClient_shouldCallSetPortOnEveryInstrument(self):
        palette.InstrumentRepository().setClient(self.client)
        for instrument in self.instruments:
            self.client.midi_outports.register.assert_any_call(instrument.name)
            instrument.setPort.assert_called_once_with(
                    self.client.midi_outports.register())


class InstrumentTests(unittest.TestCase):

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

    def test_init_shouldCreateLoops(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        self.assertEqual(instrument.loops, self.loops)

    def test_setPort_shouldSetPort(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        self.assertEqual(self.port, instrument.port)

    def test_process_shouldClearBuffer(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        instrument.process(self.noOfFrames)
        self.port.clear_buffer.assert_called_once()

    def test_process_shouldPlayNonStickyNotes(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        instrument.setPort(self.port)
        instrument.keyPressed(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(0,
                (palette.PLAY_NOTE_EVENT + self.channel1, self.note1,
                    palette.DEFAULT_VEL))
        self.port.reset_mock()
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(0,
                (palette.STOP_NOTE_EVENT + self.channel1, self.note1,
                    palette.DEFAULT_VEL))

    def test_process_shouldPlayStickyNotes(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=True)
        instrument.setPort(self.port)
        instrument.keyPressed(self.key1)
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(0,
                (palette.PLAY_NOTE_EVENT + self.channel1, self.note1,
                    palette.DEFAULT_VEL))
        self.port.reset_mock()
        instrument.keyPressed(self.key1)
        instrument.keyReleased(self.key1)
        instrument.process(self.noOfFrames)
        self.port.write_midi_event.assert_called_once_with(0,
                (palette.STOP_NOTE_EVENT + self.channel1, self.note1,
                    palette.DEFAULT_VEL))
                
    def test_process_shouldCallProcessOnEachLoop(self):
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

    def test_process_shouldQuantiseSnapNotesToGivenBeats(self):
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

    def test_process_shouldOutputEventsProducedByLoops(self):
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

    def test_deleteMode_shouldCallClearOnTheGivenLoop(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = False
        instrument.deleteMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].clear.assert_called_once()

    def test_deleteMode_shouldNotCallClearIfTheLoopIsPlaying(self):
        instrument = palette.Instrument(name=self.name,
                                        mapping=self.mapping,
                                        snap=False,
                                        sticky=False)
        loopNumber = 0
        self.loops[loopNumber].playing = True
        instrument.deleteMode()
        instrument.loop(loopNumber)
        self.loops[loopNumber].clear.assert_not_called()

    def test_recordMode_shouldCallStartRecordingIfLoopIsNotRecording(self):
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

    def test_recordMode_shouldCallStopRecordingIfLoopIsRecording(self):
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

    def test_recordMode_shouldDoNothingIfLoopIsPlaying(self):
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

    def test_recordMode_shouldQuantiseStartRecordingToGivenBeats(self):
        self.fail()

    def test_recordMode_shouldQuantiseStopRecordingToGivenBeats(self):
        self.fail()

    def test_halfMode_shouldCallHalfOnGivenLoop(self):
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

    def test_doubleMode_shouldCallDoubleOnGivenLoop(self):
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

    def test_normalMode_shouldCallPlayIfLoopIsNotPlaying(self):
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

    def test_normalMode_shouldCallStopIfLoopIsPlaying(self):
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

    def test_normalMode_shouldQuantisePlayToGivenBeats(self):
        self.fail()

    def test_normalMode_shouldQuantiseStopToGivenBeats(self):
        self.fail()


class BackendTests(unittest.TestCase):

    def setUp(self):
        palette.Backend.__INSTANCE__ = None
        self.jack = patchHandler(self, 'jack')
        self.instRepo = patchHandler(self, 'InstrumentRepository')
        self.metronome = patchHandler(self, 'Metronome')
        self.backend = palette.Backend()
        self.noOfFrames = 10

    def test_init_shouldAlwaysReturnSameInstance(self):
        self.assertIsNotNone(self.backend)
        self.assertEqual(self.backend, palette.Backend())

    def test_init_shouldInitJackClient(self):
        self.jack.Client.assert_called_once_with(palette.CLIENT_NAME,
                                                 no_start_server=True)

    def test_init_shouldSetClientOnInstrumentRepository(self):
        self.instRepo().setClient.assert_called_once_with(self.jack.Client())

    def test_init_shouldSetShutdownCallback(self):
        self.jack.Client().set_shutdown_callback.assert_called_once_with(
                self.backend.shutdown)

    def test_init_shouldSetProcessCallback(self):
        self.jack.Client().set_process_callback.assert_called_once_with(
                self.backend.process)

    def test_init_shouldActivateClient(self):
        self.jack.Client().activate.assert_called_once()

    def test_shutdown_shouldDeactivateClient(self):
        self.backend.shutdown()
        self.jack.Client().deactivate.assert_called_once()

    def test_shutdown_shouldCloseClient(self):
        self.backend.shutdown()
        self.jack.Client().close.assert_called_once()

    def test_process_shouldProcessMetronome(self):
        self.backend.process(self.noOfFrames)
        self.metronome().process.assert_called_once_with(self.noOfFrames)

    def test_process_shouldProcessInsturmentRepository(self):
        self.backend.process(self.noOfFrames)
        self.instRepo().process.assert_called_once_with(self.noOfFrames)


class MainFunctionTests(unittest.TestCase):

    def setUp(self):
        palette.EXITING = False
        self.mockMain = patchHandler(self, 'Main')
        self.mockThreading = patchHandler(self, 'threading')
        self.mockSys = patchHandler(self, 'sys')
        self.mainThread = threading.Thread(target=palette.main, daemon=True)
        self.mockSys.argv = ['scriptName']

    def tearDown(self):
        palette.EXITING = True

    def test_main_shouldStartDriverThreadIfTestOptionNotGiven(self):
        self.mainThread.start()
        self.mockThreading.Thread.assert_called_once_with(target=palette.driver,
                daemon=True)
        self.mockThreading.Thread().start.assert_called_once()

    def test_main_shouldNotStartDriverThreadIfTestOptionGiven(self):
        self.mockSys.argv.append('-t')
        self.mainThread.start()
        self.mockThreading.Thread.assert_not_called()

    def test_main_shouldCallKeyPressedIfLineStartsWithPlus(self):
        key = 5
        self.mockMain().fifo.readline.return_value = '+{0}'.format(key)
        self.mainThread.start()
        self.mockMain().keyPressed.assert_called_with(key)

    def test_main_shouldCallKeyReleasedIfLineStartWithMinus(self):
        key = 5
        self.mockMain().fifo.readline.return_value = '-{0}'.format(key)
        self.mainThread.start()
        self.mockMain().keyReleased.assert_called_with(key)


class DriverTests(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
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
    unittest.TextTestRunner(verbosity=2).run(suite)
