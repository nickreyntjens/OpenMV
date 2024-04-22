# source: https://github.com/bolderflight/sbus/blob/main/src/sbus.cpp
from sbus_constants import PAYLOAD_LEN_, HEADER_LEN_, FOOTER_LEN_, NUM_SBUS_CH_, HEADER_, FOOTER_, FOOTER2_, CH17_MASK_, CH18_MASK_, LOST_FRAME_MASK_, FAILSAFE_MASK_
from pyb import UART

class SbusTx:
    def __init__(self, uart):
        print('initializing sbus tx')
        self.buf_ = bytearray(25)
        self.uart_ = uart

    def send(self, sbus_packet):
        self.data_to_buff(sbus_packet, self.buf_)
        b = bytes(self.buf_)
        print('sending bytes', b)
        self.uart_.write(b)

    def data_to_buff(self, data_, buf_):
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
        # buf_[23] = 0x00 | (data_.ch[17] * CH17_MASK_) | (data_.ch[18] * CH18_MASK_) | (data_.failsafe * FAILSAFE_MASK_) | (data_.lost_frame * LOST_FRAME_MASK_)
        buf_[24] = FOOTER_
