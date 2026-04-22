from struct import pack

class ByteWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.current_byte = 0
        self.bit_pos = 0

    def write_bool(self, value: bool):
        if value:
            self.current_byte |= (1 << self.bit_pos)
        self.bit_pos += 1
        if self.bit_pos == 8:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_pos = 0

    def align_to_byte(self):
        if self.bit_pos > 0:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_pos = 0

    def write_int(self, value: int, length: int = 0):
        self.align_to_byte()
        if length:
            self.buffer.extend(value.to_bytes(length, 'big'))
        else:
            if value == 0:
                self.buffer.append(0)
                return
            while value > 0:
                byte = value & 0x7F
                value >>= 7
                if value > 0:
                    byte |= 0x80
                self.buffer.append(byte)

    def write_float(self, value: float):
        self.align_to_byte()
        self.buffer.extend(pack('<f', value))

    def write_string(self, s: str):
        utf8_bytes = s.encode('utf-8')
        self.write_int(len(utf8_bytes), 1)
        self.buffer.extend(utf8_bytes)

    def write_keydata(self, flags: list[int]):
        flag_byte = 0
        data_bytes = bytearray()
        for i, val in enumerate(flags):
            if val:
                flag_byte |= (1 << i)
                data_bytes.append(val)
        total_len = 1 + len(data_bytes)
        self.write_int(total_len, 1)
        self.write_int(flag_byte, 1)
        self.buffer.extend(data_bytes)

    def get_bytes(self) -> bytes:
        self.align_to_byte()
        return bytes(self.buffer)