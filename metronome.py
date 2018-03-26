import jack

from interface import SUBBEATS_PER_BEAT

class Metronome:
    def __init__(self, display, client):
        self.display = display
        self.client = client

    def transport_on(self):
        return self.client.transport_state != jack.STOPPED

    def toggle_transport(self):
        if self.transport_on():
            self.client.transport_stop()
        else:
            self.client.transport_start()

    def process(self):
        state, position = self.client.transport_query()
        self.display.log(str(position))

        if not self.transport_on():
            self.display.change_beat_data(0,0,0)
            return

        try:
            self.display.change_beat_data(int(position["beats_per_bar"]),
                    int(position["beat_type"]),
                    position["beats_per_minute"])

            beat = int(position["beat"]) - 1 # -1 to compensate for enumeration starting at 1
            tick_in_beat = int(position["tick"])
            ticks_per_beat = position["ticks_per_beat"]
            current_sub_beat = tick_in_beat // (ticks_per_beat / SUBBEATS_PER_BEAT)
            self.display.paint_active_tick(int(beat * SUBBEATS_PER_BEAT + current_sub_beat))
        except KeyError:
            return

    def timemaster(state, blocksize, position, is_new):
        pass

    def sync_transport(self):
        state, struct = self.client.transport_query_struct()
        struct.bar = 1
        struct.beat = 1
        struct.beat_type = 4
        struct.beats_per_bar = 4
        struct.beats_per_minute = 120
        struct.ticks_per_beat = 1920
        struct.valid = 16
        self.client.transport_reposition_struct(struct)

    def decrement_bpm(self):
        state, struct = self.client.transport_query_struct()
        struct.beats_per_minute = struct.beats_per_minute - 1
        self.client.transport_reposition_struct(struct)

    def increment_bpm(self):
        state, struct = self.client.transport_query_struct()
        struct.beats_per_minute = struct.beats_per_minute + 1
        self.client.transport_reposition_struct(struct)
