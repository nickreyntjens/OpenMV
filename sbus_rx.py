# source: https://github.com/bolderflight/sbus/blob/main/src/sbus.cpp
from sbus_constants import PAYLOAD_LEN_, HEADER_LEN_, FOOTER_LEN_, NUM_SBUS_CH_, HEADER_, FOOTER_, FOOTER2_, CH17_MASK_, CH18_MASK_, LOST_FRAME_MASK_, FAILSAFE_MASK_
from pyb import UART

class SbusRx:
    def __init__(self, uart):
        self.state_ = 0
        self.prev_byte_ = 0
        self.buf_ = [0] * 25
        self.uart_ = uart

    def read_latest(self, sbusPacket):
        # Read through all available packets to get the newest
        new_sbusPacket_ = False
        while self.uart_.any():
            print("Reading")
            if self.parse(sbusPacket):
                new_sbusPacket_ = True
        return new_sbusPacket_

    def parse(self, sbusPacket):
        while self.uart_.any():
            print("Reading available")
            cur_byte = self.uart_.read(1)[0]
            print('got byte', cur_byte)
            # intv = int.from_bytes(cur_byte, byteorder='little', signed=False)
            # print('got int', intv)
            if self.state_ == 0:
                if (cur_byte == HEADER_) and ((self.prev_byte_ == FOOTER_) or ((self.prev_byte_ & 0x0F) == FOOTER2_)):
                    print("header found")
                    self.buf_[self.state_] = cur_byte
                    self.state_ += 1
                else:
                    print("header not found - skipping")
                    self.state_ = 0
            elif self.state_ < PAYLOAD_LEN_ + HEADER_LEN_:
                print("filling buff")
                self.buf_[self.state_] = cur_byte
                self.state_ += 1
            elif self.state_ < PAYLOAD_LEN_ + HEADER_LEN_ + FOOTER_LEN_:
                print("almost parsing buff")
                self.state_ = 0
                self.prev_byte_ = cur_byte
                if (cur_byte == FOOTER_) or ((cur_byte & 0x0F) == FOOTER2_):
                    if self.parse_buffer(sbusPacket):
                        return True
                    else:
                        return False
            else:
                self.state_ = 0
            self.prev_byte_ = cur_byte
        return False

    def parse_buffer(self, sbusPacket):
        print("Parsing buffer")
        buf_ = self.buf_

        # Grab the channel sbusPacket
        sbusPacket.ch[0] = int.from_bytes([buf_[1], buf_[2] & 0x07], byteorder='little', signed=False)
        sbusPacket.ch[1] = int.from_bytes([(buf_[2] >> 3) | (buf_[3] << 5) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[2] = int.from_bytes([(buf_[3] >> 6) | (buf_[4] << 2) | ((buf_[5] << 10) & 0x07FF)], byteorder='little', signed=False)
        sbusPacket.ch[3] = int.from_bytes([(buf_[5] >> 1) | (buf_[6] << 7) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[4] = int.from_bytes([(buf_[6] >> 4) | (buf_[7] << 4) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[5] = int.from_bytes([(buf_[7] >> 7) | (buf_[8] << 1) | ((buf_[9] << 9) & 0x07FF)], byteorder='little', signed=False)
        sbusPacket.ch[6] = int.from_bytes([(buf_[9] >> 2) | (buf_[10] << 6) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[7] = int.from_bytes([(buf_[10] >> 5) | (buf_[11] << 3) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[8] = int.from_bytes([buf_[12], (buf_[13] << 8) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[9] = int.from_bytes([(buf_[13] >> 3) | (buf_[14] << 5) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[10] = int.from_bytes([(buf_[14] >> 6) | (buf_[15] << 2) | ((buf_[16] << 10) & 0x07FF)], byteorder='little', signed=False)
        sbusPacket.ch[11] = int.from_bytes([(buf_[16] >> 1) | (buf_[17] << 7) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[12] = int.from_bytes([(buf_[17] >> 4) | (buf_[18] << 4) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[13] = int.from_bytes([(buf_[18] >> 7) | (buf_[19] << 1) | ((buf_[20] << 9) & 0x07FF)], byteorder='little', signed=False)
        sbusPacket.ch[14] = int.from_bytes([(buf_[20] >> 2) | (buf_[21] << 6) & 0x07FF], byteorder='little', signed=False)
        sbusPacket.ch[15] = int.from_bytes([(buf_[21] >> 5) | (buf_[22] << 3) & 0x07FF], byteorder='little', signed=False)
        #sbusPacket.ch[16] = buf_[23] & 0x0001
        #sbusPacket.ch[17] = buf_[23] & 0x0002
        #sbusPacket.lost_frame = buf_[23] & LOST_FRAME_MASK_
        #sbusPacket.failsafe = buf_[23] & FAILSAFE_MASK_
        return True
