# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#

import time
import pyb
from pyb import UART
from stm import mem32

from sbus_packet import SbusPacket
from sbus_tx import SbusTx
from sbus_rx import SbusRx
from sbus_reciever import SBUSReceiver
from machine import LED

led = LED("LED_BLUE")
def blink():
    type = time.ticks_ms() % 5000 > 2500 # only updates per 1000 ms!
    if type:
        led.on()
    else:
        led.off()

# from sbus_rx import SbusRx

# The SBUS protocol uses an
# inverted serial logic with a baud rate of 100000, 8 data bits,
# even parity, and 2 stop bits
# https://docs.openmv.io/library/machine.UART.html
baud=115200 # +- 100 bit per millisecond - sbus is 25 * 8 = 200 bits ... so take 2 milliseconds
            # so 1ms silence, 2 ms signal, 1 ms silence, 2 ms signal, 1 ms silence, 2 ms signal, 1 ms silence, 2 ms signal
            # is a realistic signal
uart = UART(1, baud, timeout_char=1000) # UART.INV_TX
uart.init(baud, bits=8, parity=0, stop=2, timeout_char=3, read_buf_len=250) # , invert=True init with given parameters



# Set the UART TX pin to be inverted.
# See the reference manual for the STM32H743VIT6, section 48.8.3, USART control register 2 (USART_CR2).
# https://www.st.com/resource/en/reference_manual/dm00314099-stm32h742-stm32h743-753-and-stm32h750-value-line-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf

# 0x40011000 - 0x400113FF USART1 Section 48.8: USART registers
# 0x540004400 - 0x400047FF USART2 Section 48.8: USART registers
# 0x40004800 - 0x40004BFF USART3 Section 48.8: USART registers
# 0x40004C00 - 0x40004FFF UART4 Section 48.8: USART registers
# 0x40005000 - 0x400053FF UART5 Section 48.8: USART registers
# 0x40011400 - 0x400117FF USART6 Section 48.8: USART registers
# 0x40007800 - 0x40007BFF UART7 Section 48.8: USART registers
# 0x40007C00 - 0x40007FFF UART8 Section 48.8: USART registers

base_address = 0x40011000
mem32[base_address + 0x4] = mem32[base_address + 0x4] | (0x3 << 16) # TX and RX pin inversion  # set rx inverted.

send_tx = True

def send_tx_data(timer):
    global send_tx
    print('in timer')
    send_tx = True

# Init Rx Timing at 300us (Frsky specific)
timTx = pyb.Timer(2)
timTx.init(period=50, callback=send_tx_data) # every 3ms

def main0():
    print('c')
    clock = time.clock()  # Create a clock object to track the FPS.



    sbusTx = SbusTx(uart)
    sbusRx = SbusRx(uart)
    sbusPacket = SbusPacket()
    sbusPacketRx = SbusPacket()
    sbusReciever2 = SBUSReceiver(uart)
    # Initialise to 0 values
    # Still need to do mapping

    while True:
        #print('e')
        clock.tick()
        type = time.ticks_ms() % 5000 > 2500 # only updates per 1000 ms!
        # print('ms', time.ticks_ms())
        # print('type', type)
        sbusPacket.ch[0] = 0
        sbusPacket.ch[1] = 0
        if type:
            # 172 - 1811
            sbusPacket.ch[0] = 1810
            sbusPacket.ch[1] = 0
        else:
            sbusPacket.ch[0] = 0
            sbusPacket.ch[1] = 1810

        blink()
        if send_tx:
            sbusTx.send(sbusPacket)
            send_tx = False
        print('in loop ', send_tx)

        # sbusReciever2.get_new_data()
        # print('recieved', sbus.get_rx_channels())

