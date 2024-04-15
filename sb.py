# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Absolute Optical Flow Translation
#
# This example shows off using your OpenMV Cam to measure translation
# in the X and Y direction by comparing the current and a previous
# image against each other. Note that only X and Y translation is
# handled - not rotation/scale in this mode.
#
# To run this demo effectively please mount your OpenMV Cam on a steady
# base and SLOWLY translate it to the left, right, up, and down and
# watch the numbers change. Note that you can see displacement numbers
# up +- half of the hoizontal and vertical resolution.
#
# NOTE You have to use a small power of 2 resolution when using
# find_displacement(). This is because the algorithm is powered by
# something called phase correlation which does the image comparison
# using FFTs. A non-power of 2 resolution requires padding to a power
# of 2 which reduces the usefulness of the algorithm results. Please
# use a resolution like B64X64 or B64X32 (2x faster).
#
# Your OpenMV Cam supports power of 2 resolutions of 64x32, 64x64,
# 128x64, and 128x128. If you want a resolution of 32x32 you can create
# it by doing "img.pool(2, 2)" on a 64x64 image.

import sensor
import time
from pyb import UART

uart = UART(3, 9600, timeout_char=1000)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=2, timeout_char=1000) # init with given parameters

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.B64X64)  # Set frame size to 64x64... (or 64x32)...
sensor.skip_frames(time=2000)  # Wait for settings take effect.
clock = time.clock()  # Create a clock object to track the FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now.
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.RGB565)
extra_fb.replace(sensor.snapshot())

class Data:
    def __init__(self, ch, failsafe, lost_frame, ch17, ch18):

        self.ch = ch
        self.failsafe = failsafe
        self.lost_frame = lost_frame
        self.ch17 = ch17
        self.ch18 = ch18

def sendSbusData(data_):
    HEADER_ = 0x55
    FOOTER_ = 0xAA
    CH17_MASK_ = 0x01
    CH18_MASK_ = 0x02
    FAILSAFE_MASK_ = 0x04
    LOST_FRAME_MASK_ = 0x08
    buf_ = bytearray(25)  # Assuming buf_ is a bytearray or a list
    buf_[0] = HEADER_
    buf_[1] = (data_.ch[0] & 0x07FF)
    buf_[2] = (data_.ch[0] & 0x07FF) >> 8 | (data_.ch[1] & 0x07FF) << 3
    buf_[3] = (data_.ch[1] & 0x07FF) >> 5 | (data_.ch[2] & 0x07FF) << 6
    buf_[4] = (data_.ch[2] & 0x07FF) >> 2
    buf_[5] = (data_.ch[2] & 0x07FF) >> 10 | (data_.ch[3] & 0x07FF) << 1
    buf_[6] = (data_.ch[3] & 0x07FF) >> 7 | (data_.ch[4] & 0x07FF) << 4
    buf_[7] = (data_.ch[4] & 0x07FF) >> 4 | (data_.ch[5] & 0x07FF) << 7
    buf_[8] = (data_.ch[5] & 0x07FF) >> 1
    buf_[9] = (data_.ch[5] & 0x07FF) >> 9 | (data_.ch[6] & 0x07FF) << 2
    buf_[10] = (data_.ch[6] & 0x07FF) >> 6 | (data_.ch[7] & 0x07FF) << 5
    buf_[11] = (data_.ch[7] & 0x07FF) >> 3
    buf_[12] = (data_.ch[8] & 0x07FF)
    buf_[13] = (data_.ch[8] & 0x07FF) >> 8 | (data_.ch[9] & 0x07FF) << 3
    buf_[14] = (data_.ch[9] & 0x07FF) >> 5 | (data_.ch[10] & 0x07FF) << 6
    buf_[15] = (data_.ch[10] & 0x07FF) >> 2
    buf_[16] = (data_.ch[10] & 0x07FF) >> 10 | (data_.ch[11] & 0x07FF) << 1
    buf_[17] = (data_.ch[11] & 0x07FF) >> 7 | (data_.ch[12] & 0x07FF) << 4
    buf_[18] = (data_.ch[12] & 0x07FF) >> 4 | (data_.ch[13] & 0x07FF) << 7
    buf_[19] = (data_.ch[13] & 0x07FF) >> 1
    buf_[20] = (data_.ch[13] & 0x07FF) >> 9 | (data_.ch[14] & 0x07FF) << 2
    buf_[21] = (data_.ch[14] & 0x07FF) >> 6 | (data_.ch[15] & 0x07FF) << 5
    buf_[22] = (data_.ch[15] & 0x07FF) >> 3
    buf_[23] = 0x00 | (data_.ch[17] * CH17_MASK_) | (data_.ch[18] * CH18_MASK_) | (data_.failsafe * FAILSAFE_MASK_) | (data_.lost_frame * LOST_FRAME_MASK_)
    buf_[24] = FOOTER_
    uart.write(buf_)


while True:

    # Example data
    data_ = Data([0] * 19, 1, 0, 1, 0)






    clock.tick()  # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot()  # Take a picture and return the image.

    # For this example we never update the old image to measure absolute change.
    displacement = extra_fb.find_displacement(img)

    # Offset results are noisy without filtering so we drop some accuracy.
    sub_pixel_x = int(displacement.x_translation() * 5) / 5.0
    sub_pixel_y = int(displacement.y_translation() * 5) / 5.0

    if (
        displacement.response() > 0.05
    ):  # Below 0.1 or so (YMMV) and the results are just noise.
        print(
            "{0:+f}x {1:+f}y {2} {3} FPS".format(
                sub_pixel_x, sub_pixel_y, displacement.response(), clock.fps()
            )
        )
    else:
        print(clock.fps())
