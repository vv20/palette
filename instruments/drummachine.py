import jack

from instruments.instrument import Instrument

BEATS_PER_BAR=16
ACCENT_INCREMENT=50

class DrumMachine(Instrument):
    def __init__(self, port, samplerate):
        super().__init__(port, samplerate)
        self.beat_bindings = []
        for i in range(0, BEATS_PER_BAR):
            self.beat_bindings.append(set())
        self.muted = set()
        self.current_beat = 0
        self.bpm = 120.0
        self.samplerate = samplerate
        self.frames_since = 0
        self.frames_per_beat = 60 / self.bpm / BEATS_PER_BAR * samplerate
        self.frames_until = self.frames_per_beat
        self.current_function = self.bind_sample
        self.control = {
            30: self.fill_all,
            31: self.fill_half,
            32: self.fill_quarter,
            33: self.fill_eighth,
            20: self.mute,
            26: self.unmute,
            8: self.clear
        }
        self.samples = {
                4: 37, # rim shot
                22: 39, # clap
                7: 56, # cowbell
                9: 49, # cymbal
                10: 46, # open hihat
                11: 42, # closed hihat
                13: 75, # claves
                14: 70, # maracas
                29: 0, # accent
                27: 35, # bass kick
                6: 38, # snare
                25: 45, # low tom
                5: 47, # med tom
                17: 50, # high tom
                16: 64, # low conga
                54: 62, # mid conga
                55: 63 # high conga
        }

    def process(self, no_frames):
        self.midi_port.clear_buffer()
        # if the beat falls within this round
        if (self.frames_until < no_frames):
            samples_to_play = self.beat_bindings[self.current_beat]
            
            # check if there is an accent on this beat
            accent = False
            if 0 in samples_to_play:
                accent = True
                samples_to_play.remove(0)

            for sample in samples_to_play:
                if sample not in self.muted:
                    if accent:
                        self.midi_port.write_midi_event(frames_until, 
                                (144, sample, 1 + ACCENT_INCREMENT))
                    else:
                        self.midi_port.write_midi_event(self.frames_until, (144, sample, 1))

            # set the counts to what they will be at the beginning of next round
            self.frames_since = int(no_frames - self.frames_until)
            self.frames_until = int(self.frames_per_beat - self.frames_since)
            self.current_beat = int((self.current_beat + 1) % BEATS_PER_BAR)
        else:
            self.frames_since += no_frames
            self.frames_until -= no_frames
    
    def key_pressed(self, key):
        if key in self.control:
            self.current_function = self.control[key]
        if key in self.samples:
            self.current_function(key)

    def key_released(self, key):
        if key in self.control:
            self.current_function = self.bind_sample

    def bind_sample(self, sample):
        set_in_question = None
        if self.frames_since < self.frames_until:
            set_in_question = self.beat_bindings[self.current_beat]
        else:
            set_in_question = self.beat_bindings[(self.current_beat + 1) % BEATS_PER_BAR]
        if sample in set_in_question:
            set_in_question.remove(sample)
        else:
            set_in_question.add(sample)

    def fill_all(self, sample):
        for i in range(0, BEATS_PER_BAR):
            self.beat_bindings[(self.current_beat + i) % BEATS_PER_BAR].add(sample)

    def fill_half(self, sample):
        for i in range(0, BEATS_PER_BAR, 2):
            self.beat_bindings[(self.current_beat + i) % BEATS_PER_BAR].add(sample)

    def fill_quarter(self, sample):
        for i in range(0, BEATS_PER_BAR, 4):
            self.beat_bindings[(self.current_beat + i) % BEATS_PER_BAR].add(sample)

    def fill_eighth(self, sample):
        for i in range(0, BEATS_PER_BAR, 8):
            self.beat_bindings[(self.current_beat + i) % BEATS_PER_BAR].add(sample)

    def mute(self, sample):
        self.muted.add(sample)

    def unmute(self, sample):
        if sample in self.muted:
            self.muted.remove(sample)

    def clear(self, sample):
        for beat in self.beat_bindings:
            if sample in beat:
                beat.remove(sample)
