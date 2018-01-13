from usb import core as usb
import usb.util as util

# set up the usb magic
keyboard = usb.find(bDeviceClass=0)
firstInt = keyboard[0][(0,0)].bInterfaceNumber

for config in keyboard:
    for interface in config:
        if keyboard.is_kernel_driver_active(interface.bInterfaceNumber):
            keyboard.detach_kernel_driver(interface.bInterfaceNumber);
            print("detaching a kernel driver")

keyboard.set_configuration()
endpoint = keyboard[0][(0,0)][0]

# open the fifo for writing
fifo = open("palette.pipe", mode="w")

attempts = 10
data = None
pressed_keys = []
while attempts > 0:
    try:
        data = keyboard.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
        if data == None:
            continue
        # clean up the keys that have been released
        for key in pressed_keys:
            if key not in data:
                pressed_keys.remove(key)
                try:
                    print("-" + str(key), file=fifo, flush=True)
                except BrokenPipeError:
                    continue
        # trigger the pressed keys
        for i in range(2, len(data)):
            if data[i] == 0:
                continue
            if data[i] not in pressed_keys:
                pressed_keys.append(data[i])
                try:
                    print("+" + str(data[i]), file=fifo, flush=True)
                except BrokenPipeError:
                    continue
    except usb.USBError as e:
        data = None
        if e.args == ("Operation timed out",):
            attempts -= 1
            print("timeout")
