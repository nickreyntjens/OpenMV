
import sensor
import time
from machine import LED

led = LED("LED_BLUE")

# from sbus_packet import SbusPacket

def main_helloworld():
    # clock = time.clock()  # Create a clock object to track the FPS.
    while True:
        led.on()
        time.sleep_ms(500)
        led.off()
        time.sleep_ms(500)
        print("Camera is running")
        # print(clock.fps())
