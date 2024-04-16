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
from sbus_constants import SbusPacket
from sbus_tx import SbusTx
from sbus_rx import SbusRx

clock = time.clock()  # Create a clock object to track the FPS.
sbusTx = SbusTx(3)
sbusRx = SbusRx(4)
sbusPacket = SbusPacket()
// Initialise to 0 values
// Still need to do mapping

while True:
    sbusRx.readLatest(sbusPacket)
    print(sbusPacket.ch[0], sbusPacket.ch[1], sbusPacket.ch[2], sbusPacket.ch[3])
    cameraHasControl = sbusPacket.ch[17]
    if !cameraHasControl:
        sbusTx.send(data_)
    else:
        print("Camera has control")
        // pitch = last_set_pitch -- Simple to ask
        // roll = last_set_roll -- Simple to ask

        // If it are all too high, you have the control to remote
        // if pitch > 5 or pitch < -5 or roll > 5 or roll < -5:
        //     sbusPacket.setPitch(0)
        //     sbusPacket.setRoll(0)
        //     sbusTx.send(data_)


        // Locate the target and modify yaw
        // targetX, targetY = find_target()
        // If no target found, then do use remote control
        // if targetX == null:
        //     sbusTx.send(data_)


        // x_,y_ = applyPitchAndRollCorrectionXY(x,y,pitch,roll)

        // dyaw = calculate_dyaw(targetX)
        // Use the magneto Meter to mix in roll

        // dthrottle = calculate_dthrottle(y_)
        // if dyaw < 2 and dthrottle < 2:
        //      targetRX, targetRY = find_target_reflection()
        //      before_or_afterness = calculate_distance_from_setpoint(targetRX,rSetPoint) // Before or after the desired point
        //      if before_or_afterness > 0:
        //          sbusPacket.setPitch(2)
        //      else:
        //          sbusPacket.setPitch(-2)

    print(clock.fps())
