"""
MicroPython for micro:bit Aosong AM2320 I2C driver
https://github.com/mcauser/microbit-am2320

MIT License
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import ustruct
import time

class AM2320:
    def __init__(self, i2c=None, address=0x5c):
        self.i2c = i2c
        self.address = address
        self.buf = bytearray(8)
    def measure(self):
        # wake sensor
        try:
            self.i2c.write(self.address, b'')
        except OSError:
            pass
        # read 4 registers starting at offset 0x00
        self.i2c.write(self.address, b'\x03\x00\x04')
        # wait at least 1.5ms
        time.sleep_ms(2)
        # read data
        buf = self.i2c.read(self.address, 8)
        crc = ustruct.unpack('<H', bytearray(buf[-2:]))[0]
        if (crc != self.crc16(buf[:-2])):
            raise Exception("checksum error")
        self.buf = buf
    def crc16(self, buf):
        crc = 0xFFFF
        for c in buf:
            crc ^= c
            for i in range(8):
                if crc & 0x01:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    def humidity(self):
        return (self.buf[2] << 8 | self.buf[3]) * 0.1
    def temperature(self):
        t = ((self.buf[4] & 0x7f) << 8 | self.buf[5]) * 0.1
        if self.buf[4] & 0x80:
            t = -t
        return t
