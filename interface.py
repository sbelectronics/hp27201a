# HP27201A speech output module, serial and terminal interfaces
# Scott Baker, http://www.smbaker.com/

# This file implements a couple of interfaces that can be used
# for controlling the module over a serial port, or by outputting
# the commands to the terminal (for debugging)

from __future__ import print_function

import string
from globals import ERROR, WARNING, INFO, DEBUG

class TimeoutException(Exception):
    pass


class ScreenInterface():
    def __init__(self):
        pass

    def execute(self, command):
        print(command.replace("\x1B", "<ESC>").replace("\x11", "<XON>"))


class SerialInterface():
    def __init__(self, port="/dev/ttyUSB0", baud=9600, timeout=5, verbosity=INFO):
        import serial
        self.port = port
        self.ser = serial.Serial(port, baud, timeout=timeout)
        self.verbosity = verbosity

    def execute(self, command):
        if self.verbosity >= DEBUG:
            print("SER> %s" % command.replace("\x1B", "<ESC>").replace("\x11", "<XON>"))            
        self.ser.write(command)

    def getResponse(self, until='\x0D'):
        s = ""
        while True:
            x = self.ser.read(1)
            if not x:
                raise TimeoutException("timeout while getting response")
            if x == until:
                return s
            s = s + x
        return s

    def hexDumper(self):
        while True:
            x = self.ser.read()
            if (x in string.printable):
                print("%02X %c" % (ord(x), x))
            else:
                print("%02X " % ord(x))
