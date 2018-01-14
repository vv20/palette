import curses

class Interface:
    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.start_color()

        self.screen.clear()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.screen.addstr("|    | F# | G# | A# |    | C# | D# |    | F# | G# |\n")
        self.screen.addstr(" | F  | G  | A  | B  | C  | D  | E  | F  | G  | A  |\n")
        self.screen.addstr("  |    | C# | D# |    | F# | G# | A# |    | C# | D# |\n")
        self.screen.addstr("   | C  | D  | E  | F  | G  | A  | B  | C  | D  | E  |\n")
        self.screen.refresh()

    def paint_key_on(self, key):
        self.screen.addstr(self.x_mappings[key], self.y_mappings[key], 
                self.string_mappings[key], curses.color_pair(1))
        self.screen.move(4,0)
        self.screen.refresh()

    def paint_key_off(self, key):
        self.screen.addstr(self.x_mappings[key], self.y_mappings[key], 
                self.string_mappings[key], curses.color_pair(0))
        self.screen.move(4,0)
        self.screen.refresh()

    def shutdown(self):
        curses.echo()
        curses.endwin()

    x_mappings = {
            31: 0,
            32: 0,
            33: 0,
            35: 0,
            36: 0,
            38: 0,
            39: 0,
            20: 1,
            26: 1,
            8: 1,
            21: 1,
            23: 1,
            28: 1,
            24: 1,
            12: 1,
            18: 1,
            19: 1,
            22: 2,
            7: 2,
            10: 2,
            11: 2,
            13: 2,
            15: 2,
            51: 2,
            29: 3,
            27: 3,
            6: 3,
            25: 3,
            5: 3,
            17: 3,
            16: 3,
            54: 3,
            55: 3,
            56: 3
    }

    y_mappings = {
            31: 6,
            32: 11,
            33: 16,
            35: 26,
            36: 31,
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
            22: 8,
            7: 13,
            10: 23,
            11: 28,
            13: 33,
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

    string_mappings = {
            31: " F# ",
            32: " G# ",
            33: " A# ",
            35: " C# ",
            36: " D# ",
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
            22: " C# ",
            7: " D# ",
            10: " F# ",
            11: " G# ",
            13: " A# ",
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
