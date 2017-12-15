import usb.core as usb
import usb.util as util
import keyboard
import sampler

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
        16: 47
        # C-,
        54: 48,
        # C#-l
        15: 49,
        # D-.
        55: 50,
        # D#-;
        51: 51,
        # E-/
        56: 52
}

# main pad
pad = range(4, 40)
pad.append(54)
pad.append(55)
pad.append(56)
pad.append(51)

def get_midi_key(int_key):
    pass

def get_track_no(int_key):
    pass

def key_released(key):
    print("key " + str(key) + " released")
    if key in pad:
        if mode == KEYBOARD_MODE:
            keyboard.stopKey(get_key_from_int(key))
        else:
            sampler.stopTrack(get_track_no(key))

def key_pressed(key):
    print("key " + str(key) + " pressed")
    if key in pad:
        if mode == KEYBOARD_MODE:
            keyboard.playKey(get_key_from_int(key))
        else:
            sampler.playTrack(get_track_no(key))

keyboard = usb.find(bDeviceClass=0)
firstInt = keyboard[0][(0,0)].bInterfaceNumber

for config in keyboard:
    for interface in config:
        if keyboard.is_kernel_driver_active(interface.bInterfaceNumber):
            keyboard.detach_kernel_driver(interface.bInterfaceNumber);
            print("detaching a kernel driver")

keyboard.set_configuration()
endpoint = keyboard[0][(0,0)][0]

attempts = 10
data = None
while attempts > 0:
    try:
        data = keyboard.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
        if data == None:
            continue
        # clean up the keys that have been released
        for key in pressed_keys:
            if key not in data:
                pressed_keys.remove(key)
                key_released(key)
        # trigger the pressed keys
        for i in range(2, len(data)):
            if data[i] == 0:
                continue
            if data[i] not in pressed_keys:
                pressed_keys.append(data[i])
                key_pressed(data[i])
    except usb.USBError as e:
        data = None
        if e.args == ("Operation timed out",):
            attempts -= 1
            print("timeout")
