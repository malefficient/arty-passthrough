"""
    Script to test serial devices
"""
import os
from time import sleep
from pylibftdi import Device, Driver, INTERFACE_B
def init(d):
    d.write("?\r\n")
    sleep(1)
    dev.write("Synchronized\r\n")
    sleep(1)
    dev.write("12000\r\n")
#print Driver().list_devices()
with Device(mode='t',interface_select=INTERFACE_B) as dev:
    dev.baudrate = 115200
    init(dev)
    #exit(0)
    # Send a read command to the board
    ###
    result=""
    dev.write('R 0 4\r\n')
    result += dev.read(1)
    dev.write("OK\r\n")
    print(repr(result))
    exit(0)
    result = ""
    while 1:
        # This is a non-blocking read (!!!)
        result += dev.read(1)
        print(repr(result))
