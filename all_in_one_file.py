print('a')

import time
import pyb
from pyb import UART
from stm import mem32
from pyb import UART
import array
import time
from machine import LED

led = LED("LED_BLUE")


SBUS_PAYLOAD_LEN_ = 23
SBUS_HEADER_LEN_ = 1
SBUS_FOOTER_LEN_ = 1
SBUS_NUM_SBUS_CH_ = 16
SBUS_HEADER = 0x0F
SBUS_FOOTER = 0x00
SBUS_FOOTER2 = 0x04
SBUS_CH17_MASK_ = 0x01
SBUS_CH18_MASK_ = 0x02
SBUS_LOST_FRAME_MASK_ = 0x04
SBUS_FAILSAFE_MASK_ = 0x08

def partial_method(method, instance, *args):
    def wrapper(*args2):
        return method(instance, *args, *args2)
    return wrapper


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
        has_data = self.uart.any()
        if has_data:
            self.uart.read(has_data)

        self.channels = [0] * (16 + 2 + 2) # 16 channels + 2 digital channels + 2 fail safes
        self.lastFrame = None
        self.readBytes = bytearray()
        self.last_frame_received_ticks_ms = None
        self.invalidFrames = 0

        # add time or interrupt to prove for first byte of frame
        poll_data_bound = partial_method(self.poll_data, self)
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

    def get_last_received_value(self):
        if self.lastFrame:
            self.decode_frame(self.lastFrame)
            return self.channels
        return None

    def poll_data(self): # must be called every 1 millisecond
        if self.uart.any() > 0:
            self.readBytes += self.uart.read()
            self.last_frame_received_ticks_ms = time.ticks_ms()
            if self.readBytes[0] == 0x0F and self.readBytes[24] == 0x00:
                self.lastFrame = self.readBytes
                self.readBytes = bytearray()
        if self.last_frame_received_ticks_ms is None or time.ticks_diff(time.time_ms(), self.last_frame_received_ticks_ms) > 3:
            # Clear buffer if no data received for 3 ms
            # SBUS is expected to come in frames, and then silence
            # 3ms of data, 6ms of silence, 3ms of data, 6ms of silence, ...
            self.readBytes = bytearray()

class SBUSTransmitter:
    def __init__(self, uart):
        print('initializing sbus tx')
        self.buf_ = bytearray(25)
        self.uart_ = uart

    def send(self, channels):
        self.data_to_buff(channels, self.buf_)
        # b = bytes(self.buf_) # likely remove
        print('sending bytes', self.buf_)
        self.uart_.write(self.buf_)

    def data_to_buff(self, data_, buf_):
        buf_[0] = SBUS_HEADER
        buf_[1] = (data_[0] & 0x07FF)
        buf_[2] = (data_[0] & 0x07FF) >> 8 | (data_[1] & 0x07FF) << 3
        buf_[3] = (data_[1] & 0x07FF) >> 5 | (data_[2] & 0x07FF) << 6
        buf_[4] = (data_[2] & 0x07FF) >> 2
        buf_[5] = (data_[2] & 0x07FF) >> 10 | (data_[3] & 0x07FF) << 1
        buf_[6] = (data_[3] & 0x07FF) >> 7 | (data_[4] & 0x07FF) << 4
        buf_[7] = (data_[4] & 0x07FF) >> 4 | (data_[5] & 0x07FF) << 7
        buf_[8] = (data_[5] & 0x07FF) >> 1
        buf_[9] = (data_[5] & 0x07FF) >> 9 | (data_[6] & 0x07FF) << 2
        buf_[10] = (data_[6] & 0x07FF) >> 6 | (data_[7] & 0x07FF) << 5
        buf_[11] = (data_[7] & 0x07FF) >> 3
        buf_[12] = (data_[8] & 0x07FF)
        buf_[13] = (data_[8] & 0x07FF) >> 8 | (data_[9] & 0x07FF) << 3
        buf_[14] = (data_[9] & 0x07FF) >> 5 | (data_[10] & 0x07FF) << 6
        buf_[15] = (data_[10] & 0x07FF) >> 2
        buf_[16] = (data_[10] & 0x07FF) >> 10 | (data_[11] & 0x07FF) << 1
        buf_[17] = (data_[11] & 0x07FF) >> 7 | (data_[12] & 0x07FF) << 4
        buf_[18] = (data_[12] & 0x07FF) >> 4 | (data_[13] & 0x07FF) << 7
        buf_[19] = (data_[13] & 0x07FF) >> 1
        buf_[20] = (data_[13] & 0x07FF) >> 9 | (data_[14] & 0x07FF) << 2
        buf_[21] = (data_[14] & 0x07FF) >> 6 | (data_[15] & 0x07FF) << 5
        buf_[22] = (data_[15] & 0x07FF) >> 3
        # buf_[23] = 0x00 | (data_[17] * CH17_MASK_) | (data_[18] * CH18_MASK_) | (data_.failsafe * FAILSAFE_MASK_) | (data_.lost_frame * LOST_FRAME_MASK_)
        buf_[24] = SBUS_FOOTER


led = LED("LED_BLUE")
def blink():
    type = time.ticks_ms() % 5000 > 2500 # only updates per 1000 ms!
    if type:
        led.on()
    else:
        led.off()

# 1ms silence, 2 ms signal, 1 ms silence, 2 ms signal, 1 ms silence, 2 ms signal, 1 ms silence, 2 ms signal
baud=115200 # +- 100 bit per millisecond - sbus is 25 * 8 = 200 bits ... so take 2 milliseconds
uart = UART(1, baud, timeout_char=1000) # UART.INV_TX
uart.init(baud, bits=8, parity=0, stop=2, timeout_char=3, read_buf_len=25) # , invert=True init with given parameters
# base_address = 0x40011000
# mem32[base_address + 0x4] = mem32[base_address + 0x4] | (0x3 << 16) # TX and RX pin inversion  # set rx inverted.



def send_tx_data(timer):
    global send_tx
    send_tx = True
    print('in timer', send_tx)

# Init Rx Timing at 300us (Frsky specific)
timTx = pyb.Timer(2)
timTx.init(period=50, callback=send_tx_data) # every 3ms

def main():
    print('c')
    clock = time.clock()  # Create a clock object to track the FPS.
    send_tx = True

    sbusChannels = [0] * 20

    sbusTx = SBUSTransmitter(uart)
    sbusRx = SBUSReceiver(uart)

    while True:
        # Generate an alternating signal
        type = time.ticks_ms() % 5000 > 2500 # only updates per 1000 ms!?
        sbusChannels[0] = 0
        sbusChannels[1] = 0
        if type:
            # 172 - 1811
            sbusChannels[0] = 1810
            sbusChannels[1] = 0
        else:
            sbusChannels[0] = 0
            sbusChannels[1] = 1810

        blink()
        if send_tx:
            print('sending')
            sbusTx.send(sbusChannels)
            channels_in = sbusRx.get_last_received_value()
            print('channels', channels_in)
            send_tx = False




main()
