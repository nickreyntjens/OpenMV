"""
The MIT License (MIT)
Copyright (c) 2016 Fabrizio Scimia, fabrizio.scimia@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from pyb import UART
import array
import time
import functools


# SBUS protocol structure of one frame
# 1 start byte 0x0F           (1 byte)
# 16 channels of 11 bits each (22 bytes --- 176 bits)
# 4 flags                     (1 byte)
# 1 end byte 0x00             (1 byte)
# => 25 bytes

# UART settings:    100000 baudrate, 8 data bits, even parity, 2 stop bits; or
#                   115200 baudrate, 8 data bits, even parity, 2 stop bits
#                   (unclear which one is correct --- flight controller of the drone has option 115200 baudrate, and not 100000 baudrate)

# https://www.youtube.com/watch?v=CULas2y_sXI&t=69s
# signal comes in packets: 3ms, 6ms, 3ms, 6ms, 3ms, 6ms ... 3ms, 6ms
# 3ms => signal in uart (in this time period the 25 bytes are sent)
# 6ms => no signal in uart (in this time period no bytes are sent, the uart is kept cosntant at 0V or +3.3V (or +5.0V))

# https://www.youtube.com/watch?v=IqLUHj7nJhI&t=9m20s
### => Frsky  ... uart is 0V               when no signal
### => Futaba ... uart is +3.3V (or +5.0v) when no signal

class SBUSReceiver:
    def __init__(self, uart):
        self.uart = uart
        # clean the buffer
        has_data = self.sbus.any()
        if has_data:
            self.uart.read(has_data)

        self.channels = [0] * (16 + 2 + 2) # 16 channels + 2 digital channels + 2 fail safes
        self.readBytes = bytearray()
        self.lastFrame = bytearray()
        self.last_frame_received_ticks_ms = none
        self.invalidFrames = 0

        # add time or interrupt to prove for first byte of frame
        poll_data_bound = functools.partial(self.poll_data, self)
        timProve = pyb.Timer(2)
        timProve.init(period=1, callback=poll_data_bound)  # every 1ms



    def decode_frame(self, frame):
        # HEADER
        # 22 bytes of channels (11 bits per channel)
        # 1 byte of digital channels
        # FOOTER

        if frame[0] != 0x0F or frame[-1] != 0x00:
            self.invalidFrames += 1
            return

        print("Decoding Frame", frame)

        # counters initialization
        byte_in_frame = 1 # byte 0 is the HEADER
        bit_in_frame = 0
        ch_in_channels = 0
        bit_in_channel = 0

        for i in range(0, 11 * 16):  # 11 bits per channel, 16 channels
            if frame[byte_in_frame] & (1 << bit_in_frame):
                self.channels[ch_in_channels] |= (1 << bit_in_channel)

            bit_in_frame += 1
            bit_in_channel += 1

            if bit_in_frame == 8:
                bit_in_frame = 0
                byte_in_frame += 1

            if bit_in_channel == 11:
                bit_in_channel = 0
                ch_in_channels += 1

        # Digital Channel 1 and 2 and fail safes
        self.channels[-3] = 1 if frame[-2] & (1 << 0) else 0
        self.channels[-2] = 1 if frame[-2] & (1 << 1) else 0
        self.channels[-1] = 1 if frame[-2] & (1 << 2) else 0 # FailSafe - signal lost
        self.channels[-0] = 1 if frame[-2] & (1 << 3) else 0 # FailSafe - signal fail safe

    def get_last_channels(self):
        self.decode_frame(self.lastFrame)
        return self.channels

    def poll_data(self): # must be called every 1 millisecond
        if self.uart.any() > 0:
            self.readBytes += self.uart.read()
            self.last_frame_received_ticks_ms = time.ticks_ms()
            if self.readBytes[0] == 0x0F and self.readBytes[24] == 0x00:
                self.lastFrame = self.readBytes
                self.readBytes = bytearray()
        if time.ticks_diff(time.time_ms(), self.last_frame_received_ticks_ms) > 3:
            # Clear buffer if no data received for 3 ms
            # SBUS is expected to come in frames, and then silence
            # 3ms of data, 6ms of silence, 3ms of data, 6ms of silence, ...
            self.readBytes = bytearray()
