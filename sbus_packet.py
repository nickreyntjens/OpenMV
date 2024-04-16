class SbusPacket:
    def __init__(self):
        self.ch = [0] * 16
        self.ch17 = 0
        self.ch18 = 0
        self.lost_frame = 0
        self.failsafe = 0

    def setYaw(self, yaw):
        self.ch[0] = yaw

    def setPitch(self, pitch):
        self.ch[1] = pitch

    def setRoll(self, roll):
        self.ch[2] = roll

    def setThrottle(self, throttle):
        self.ch[3] = throttle

    def getYaw(self):
        return self.ch[0]

    def getPitch(self):
        return self.ch[1]

    def getRoll(self):
        return self.ch[2]

    def getThrottle(self):
        return self.ch[3]

