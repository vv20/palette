import keyboard as keys
import sampler
import backend

KEYBOARD_MODE = 1
SAMPLER_MODE = 2
mode = KEYBOARD_MODE

pressed_keys = []

keyboard_mappings = {
        # C-z
        29: 36,
        # C#-s
        22: 37,
        # D-x
        28: 38,
        # D#-d
        7: 39,
        # E-c
        6: 40,
        # F-v
        25: 41,
        # F#-g
        10: 42,
        # G-b
        5: 43,
        # G#-h
        11: 44,
        # A-n
        17: 45,
        # A#-j
        13: 46,
        # B-m
        16: 47,
        # C-,
        54: 48,
        # C#-l
        15: 49,
        # D-.
        55: 50,
        # D#-;
        51: 51,
        # E-/
        56: 52,
        # upper keyboard
        # F-q
        20: 53,
        # F#-2
        31: 54,
        # G-w
        26: 55,
        # G#-3
        32: 56,
        # A-e
        8: 57,
        # A#-4
        33: 58,
        # B-r
        21: 59,
        # C-t
        23: 60,
        # C#-6
        35: 61,
        # D-y
        28: 62,
        # D#-7
        36: 63,
        # E-u
        24: 64,
        # F-i
        12: 65,
        # F#-9
        38: 66,
        # G-o
        18: 67,
        # G#-0
        39: 68,
        # A-p
        19: 69
}

# main pad
pad = list(range(4, 40))
pad.append(54)
pad.append(55)
pad.append(56)
pad.append(51)

def key_released(key):
    print("key " + str(key) + " released")
    if key in pad:
        if mode == KEYBOARD_MODE:
            try:
                keys.stopKey(keyboard_mappings[key])
            except KeyError:
                pass
        else:
            sampler.stopTrack(get_track_no(key))

def key_pressed(key):
    print("key " + str(key) + " pressed")
    if key in pad:
        if mode == KEYBOARD_MODE:
            try:
                keys.playKey(keyboard_mappings[key])
            except KeyError:
                pass
        else:
            sampler.playTrack(get_track_no(key))

# init the jack backend
backend.init()

# open the fifo for receiving data
fifo = open("palette.pipe", mode="rt")

while True:
    line = fifo.readline()
    if line[0] == '+':
        key_pressed(int(line[1:]))
    else:
        key_pressed(int(line[1:]))
