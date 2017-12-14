import usb.core as usb
import usb.util as util

KEYBOARD_MODE = 1
DRUMPAD_MODE = 2
SAMPLER_MODE = 3
EFFECTS_MODE = 4
LOOPER_MODE = 5
mode = KEYBOARD_MODE

pressed_keys = []

def key_released(key):
    print("key " + str(key) + " released")

def key_pressed(key):
    print("key " + str(key) + " pressed")

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
