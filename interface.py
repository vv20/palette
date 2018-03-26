import curses

from enum import Enum

SUBBEATS_PER_BEAT = 4

x_mappings = {
        30: 1,
        31: 1,
        32: 1,
        33: 1,
        34: 1,
        35: 1,
        36: 1,
        37: 1,
        38: 1,
        39: 1,
        20: 2,
        26: 2,
        8: 2,
        21: 2,
        23: 2,
        28: 2,
        24: 2,
        12: 2,
        18: 2,
        19: 2,
        4: 3,
        22: 3,
        7: 3,
        9: 3,
        10: 3,
        11: 3,
        13: 3,
        14: 3,
        15: 3,
        51: 3,
        29: 4,
        27: 4,
        6: 4,
        25: 4,
        5: 4,
        17: 4,
        16: 4,
        54: 4,
        55: 4,
        56: 4
}

y_mappings = {
        30: 1,
        31: 6,
        32: 11,
        33: 16,
        34: 21,
        35: 26,
        36: 31,
        37: 36,
        38: 41,
        39: 46,
        20: 2,
        26: 7,
        8: 12,
        21: 17,
        23: 22,
        28: 27,
        24: 32,
        12: 37,
        18: 42,
        19: 47,
        4: 3,
        22: 8,
        7: 13,
        9: 18,
        10: 23,
        11: 28,
        13: 33,
        14: 38,
        15: 43,
        51: 48,
        29: 4,
        27: 9,
        6: 14,
        25: 19,
        5: 24,
        17: 29,
        16: 34,
        54: 39,
        55: 44,
        56: 49
}

keyboard_mappings = {
        30: "    ",
        31: " F# ",
        32: " G# ",
        33: " A# ",
        34: "    ",
        35: " C# ",
        36: " D# ",
        37: "    ",
        38: " F# ",
        39: " G#",
        20: " F  ",
        26: " G  ",
        8: " A  ",
        21: " B  ",
        23: " C  ",
        28: " D  ",
        24: " E  ",
        12: " F  ",
        18: " G  ",
        19: " A  ",
        4: "    ",
        22: " C# ",
        7: " D# ",
        9: "    ",
        10: " F# ",
        11: " G# ",
        13: " A# ",
        14: "    ",
        15: " C# ",
        51: " D# ",
        29: " C  ",
        27: " D  ",
        6: " E  ",
        25: " F  ",
        5: " G  ",
        17: " A  ",
        16: " B  ",
        54: " C  ",
        55: " D  ",
        56: " E  "
}

sampler_mappings = {
        30: " 1  ",
        31: " 2  ",
        32: " 3  ",
        33: " 4  ",
        34: "    ",
        35: "    ",
        36: " C4 ",
        37: " C#4",
        38: " D4 ",
        39: " D#4",
        20: " 5  ",
        26: " 6  ",
        8: " 7  ",
        21: " 8  ",
        23: "    ",
        28: "    ",
        24: " E4 ",
        12: " F4 ",
        18: " F#4",
        19: " G4 ",
        4: " 9  ",
        22: " 10 ",
        7: " 11 ",
        9: " 12 ",
        10: "    ",
        11: "    ",
        13: " G#4",
        14: " A4 ",
        15: " A#4",
        51: " B4 ",
        29: " 13 ",
        27: " 14 ",
        6: " 15 ",
        25: " 16 ",
        5: "    ",
        17: "    ",
        16: " C5 ",
        54: " C#5",
        55: " D5 ",
        56: " D#5"
}

drummachine_mappings = {
        30: " 1/1",
        31: " 1/2",
        32: " 1/4",
        33: " 1/8",
        34: "    ",
        35: "    ",
        36: "    ",
        37: "    ",
        38: "    ",
        39: "    ",
        20: " mu ",
        26: " um ",
        8: " cl ",
        21: "    ",
        23: "    ",
        28: "    ",
        24: "    ",
        12: "    ",
        18: "    ",
        19: "    ",
        4: " RS ",
        22: " CP ",
        7: " CB ",
        9: " CY ",
        10: " OH ",
        11: " CH ",
        13: " CL ",
        14: " MA ",
        15: "    ",
        51: "    ",
        29: " AC ",
        27: " BD ",
        6: " SD ",
        25: " LT ",
        5: " MT ",
        17: " HT ",
        16: " LC ",
        54: " MC ",
        55: " HC ",
        56: "    "
}

class Entity(Enum):
    DRUM_MACHINE = 1,
    KEYBOARD = 2,
    SAMPLER = 3

entity_names = {
        Entity.DRUM_MACHINE: " DrumMac ",
        Entity.KEYBOARD: " Keyboard",
        Entity.SAMPLER: " Sampler "
}

entity_mappings = {
        Entity.DRUM_MACHINE: drummachine_mappings,
        Entity.KEYBOARD: keyboard_mappings,
        Entity.SAMPLER: sampler_mappings
}

class Interface:
    def __init__(self, entities):
        self.screen = curses.initscr()
        curses.noecho()
        curses.start_color()

        self.screen.clear()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.entities = entities
        self.active_entity = 0

        # metronome stuff
        self.beat_type = 0
        self.beats_per_bar = 0
        self.bpm = 0

    def paint_pad(self, active_entity):
        self.screen.clear()
        self.active_entity = active_entity
        # paint the headbar with the active entity highlighted
        for i in range(0, active_entity):
            self.screen.addstr("|")
            self.screen.addstr(entity_names[self.entities[i]])
        self.screen.addstr(entity_names[self.entities[active_entity]], 
                curses.color_pair(1))
        for i in range(active_entity + 1, len(self.entities)):
            self.screen.addstr("|")
            self.screen.addstr(entity_names[self.entities[i]])
        self.screen.addstr("|")
        
        # paint the pad
        maps = entity_mappings[self.entities[active_entity]]
        for key in maps:
            self.screen.addstr(x_mappings[key], y_mappings[key], "|" + maps[key])

        # paint the beat and the bpm
        self.screen.move(5,0)
        self.screen.addstr("\n")
        self.screen.addstr("Beat: " + str(self.beats_per_bar) + "/" + str(self.beat_type) + " ")
        self.screen.addstr("BPM: " + str(self.bpm) + "\n")
        
        # paint the ticks
        self.screen.addstr("-" * (self.beats_per_bar * SUBBEATS_PER_BEAT * 2 + 1))
        self.screen.addstr("\n")
        for i in range(0, self.beats_per_bar * SUBBEATS_PER_BEAT):
            self.screen.addstr("| ")
        self.screen.addstr("|\n")
        self.screen.addstr("-" * (self.beats_per_bar * SUBBEATS_PER_BEAT * 2 + 1))
        self.screen.move(10, 0)
        self.screen.refresh()

    def paint_key_on(self, key):
        maps = entity_mappings[self.entities[self.active_entity]]
        self.screen.addstr(x_mappings[key], y_mappings[key] + 1, 
                maps[key], curses.color_pair(1))
        self.screen.move(10,0)
        self.screen.refresh()

    def paint_key_off(self, key):
        maps = entity_mappings[self.entities[self.active_entity]]
        self.screen.addstr(x_mappings[key], y_mappings[key] + 1, 
                maps[key], curses.color_pair(0))
        self.screen.move(10,0)
        self.screen.refresh()

    def change_beat_data(self, beats_per_bar, beat_type, bpm):
        if beats_per_bar == self.beats_per_bar and beat_type == self.beat_type and bpm == self.bpm:
            return
        self.beats_per_bar = beats_per_bar
        self.beat_type = beat_type
        self.bpm = bpm
        self.screen.move(6,0)
        self.screen.addstr("Beat: ")
        self.screen.addstr(str(self.beats_per_bar))
        self.screen.addstr("/")
        self.screen.addstr(str(self.beat_type))
        self.screen.addstr(" BPM: ")
        self.screen.addstr(str(self.bpm))
        self.screen.addstr(" " * 10) # wipe the rest of the line
        self.screen.move(10, 0)
        self.screen.refresh()

    def paint_active_tick(self, tick_no):
        self.screen.move(8,0)
        for i in range(0, tick_no):
            self.screen.addstr("| ")
        self.screen.addstr("|")
        self.screen.addstr(" ", curses.color_pair(1))
        for i in range(tick_no + 1, SUBBEATS_PER_BEAT * self.beats_per_bar):
            self.screen.addstr("| ")
        self.screen.addstr("|")
        self.screen.move(10,0)
        self.screen.refresh()

    def log(self, msg):
        self.screen.addstr(msg)
        self.screen.move(10,0)
        self.screen.refresh()

    def shutdown(self):
        curses.echo()
        curses.endwin()
