// source: https://github.com/fdivitto/MSP/blob/master/MSP.cpp
// http://www.multiwii.com/wiki/index.php?title=Multiwii_Serial_Protocol

class MPS:
    def __init__(self, uartNr):
        self.readBytesHasHeader = False
        self.state_ = 0
        self.prev_byte__ = 0
        self.buf_ = [0] * 25
        self.incomingMessages = []
        self.readBytes = bytearray()
        self.uart_ = UART(uartPinRX, 9600, timeout_char=1000)                         # init with given baudrate
        self.uart_.init(9600, bits=8, parity=None, stop=2, timeout_char=1000)         # init with given parameters

    def requestMSP_ATTITUDE(self):
        self.send(108, [])

    def getLastMSP_ATTITUDEMsg(self):
        self.fillReplyBuffer(Okay)
        for i in range(len(self.incomingMessages) - 1, -1, -1):
            if self.incomingMessages[i][4] == 108:
                return self.incomingMessages[i]

    def send(self, messageID, payloadByteArray):
        payloadByteArrayLen = len(payloadByteArray)
        checksum = size ^ messageID
        for i in range(payloadByteArrayLen):
            checksum ^= payloadByteArray[i]
        b1 = bytes([ord('$'), ord('M'), ord('<'), payloadByteArrayLen, messageID])
        self.uartTx_.write(b1 + payloadByteArray + bytes([checksum])

    def fillReplyBuffer(self):
        self.pollIncomingMessages()
        self.parseIncomingMessages()
        # Remove messages that are too old
        while len(self.incomingMessages) > 10:
            self.incomingMessages.pop(0)

    def pollIncomingMessages(self):
        self.readBytes = self.readBytes + self.uartRx_.read()

    def parseIncomingMessages(self):
        if not self.readBytesHasHeader:
            if len(self.readBytes) > 6:
                if self.readBytes[0] == ord('$') and self.readBytes[1] == ord('M') and self.readBytes[2] == ord('<'):
                    #payloadByteArrayLen = self.readBytes[3]
                    #messageID = self.readBytes[4]
                    self.readBytesHasHeader = True
            else:
                # Search for header and drop bytes before it
                header_index = self.readBytes.find(bytes([ord('$'), ord('M'), ord('<')]))
                if header_index != -1:
                    self.readBytes = self.readBytes[header_index:]
                    self.readBytesHasHeader = True
                return
        else:
            payloadByteArrayLen = self.header[3]
            if (len(self.readBytes) >= 5 + payloadByteArrayLen + 1):
                checksumCalc = payloadByteArrayLen ^ messageID
                for i in range(payloadByteArrayLen):
                    checksumCalc ^= self.readBytes[5 + i]
                checksum = self.readBytes[5 + payloadByteArrayLen]
                if checksumCalc == checksum:
                    self.incomingMessages.append(self.readBytes[0:5 + payloadByteArrayLen + 1])
                else:
                    print("Checksum error")
                self.readBytes = self.readBytes[5 + payloadByteArrayLen + 1:]
            self.readBytesHasHeader = False

