import jack

BEATS_PER_BAR=16

class DrumMachine:
    def __init__(self, port, samplerate):
        self.beat_bindings = []
        for i in range(0, BEATS_PER_BAR):
            self.beat_bindings.append(set())
        self.muted = set()
        self.current_beat = 0
        self.bpm = 120.0
        self.samplerate = samplerate
        self.frames_since = 0
        self.frames_per_beat = 60 / self.bpm * samplerate
        self.frames_until = self.frames_per_beat
        self.midi_port = port

    def process(self, no_frames):
        # if the beat falls within this round
        if (frames_until < no_frames):
            samples_to_play = self.beat_bindings[self.current_beat]
            for sample in samples_to_play:
                if sample not in self.muted:
                    self.midi_port.write_midi_event(frames_until, (144, sample, 1))
            # set the counts to what they will be at the beginning of next round
            self.frames_since = no_frames - frames_until
            self.frames_until = self.frames_per_beat - self.frames_since
            self.current_beat = (self.current_beat + 1) % BEATS_PER_BAR
        else:
            self.frames_since += no_frames
            self.frames_until -= no_frames

    def play_sample(self, sample):
        set_in_question = None
        if self.frames_since < self.frames_until:
            set_in_question = self.beat_bindings[self.current_beat]
        else:
            set_in_question = self.beat_bindings[self.current_beat]
        if sample in set_in_question:
            set_in_question.remove(sample)
        else:
            set_in_question.add(sample)

    def fill(self, sample, fraction):
        for i in range(0, BEATS_PER_BAR, fraction):
            self.beat_bindings[(current_beat + i) % BEATS_PER_BAR].add(sample)

    def fill_all(self, sample):
        self.fill(sample, 1)

    def fill_half(self, sample):
        self.fill(sample, 2)

    def fill_quarter(self, sample):
        self.fill(sample, 4)

    def fill_eigth(self, sample):
        self.fill(sample, 8)

    def mute(self, sample):
        self.muted.add(sample)

    def unmute(self, sample):
        self.muted.remove(sample)

    def clear(self, sample):
        for beat in self.beat_bindings:
            beat.remove(sample)
