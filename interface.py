import curses

class Interface:
    def __init__(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.start_color()

        self.screen.clear()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.paint_keyboard()

    def paint_keyboard(self):
        self.screen.clear()
        self.screen.addstr("|")
        self.screen.addstr(" Keyboard ", curses.color_pair(1))
        self.screen.addstr("| Sampler |\n")
        self.screen.addstr("|    | F# | G# | A# |    | C# | D# |    | F# | G# |\n")
        self.screen.addstr(" | F  | G  | A  | B  | C  | D  | E  | F  | G  | A  |\n")
        self.screen.addstr("  |    | C# | D# |    | F# | G# | A# |    | C# | D# |\n")
        self.screen.addstr("   | C  | D  | E  | F  | G  | A  | B  | C  | D  | E  |\n")
        self.screen.refresh()

    def paint_sampler(self):
        self.screen.clear()
        self.screen.addstr("| Keyboard |")
        self.screen.addstr(" Sampler ", curses.color_pair(1))
        self.screen.addstr("|\n")
        self.screen.addstr("| 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 |\n")
        self.screen.addstr(" | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |\n")
        self.screen.addstr("  | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 |\n")
        self.screen.addstr("   | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |\n")
        self.screen.refresh()

    def paint_key_on(self, key):
        self.screen.addstr(self.x_mappings[key], self.y_mappings[key], 
                self.string_mappings[key], curses.color_pair(1))
        self.screen.move(5,0)
        self.screen.refresh()

    def paint_key_off(self, key):
        self.screen.addstr(self.x_mappings[key], self.y_mappings[key], 
                self.string_mappings[key], curses.color_pair(0))
        self.screen.move(5,0)
        self.screen.refresh()

    def shutdown(self):
        curses.echo()
        curses.endwin()

    x_mappings = {
            31: 1,
            32: 1,
            33: 1,
            35: 1,
            36: 1,
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
            22: 2,
            7: 3,
            10: 3,
            11: 3,
            13: 3,
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
