from struct import unpack

class ByteReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.bit_pos = 0

    def read_bool(self) -> bool:
        """read 1 bit to bool

        return:
            bool
        """
        self.pos += self.bit_pos // 8
        self.bit_pos %= 8
        res = bool(self.data[self.pos] & (1 << self.bit_pos))
        self.bit_pos += 1
        return res

    def align_to_byte(self):
        """finish the byte

        """
        self.pos += bool(self.bit_pos)
        self.bit_pos = 0

    def read_int(self, len: int = 0) -> int:
        """read len bytes to int

        args:
            len:
                0 to var int
                n to n byte

        return:
            int
        """
        self.align_to_byte()
        if len:
            res = int.from_bytes(self.data[self.pos:self.pos + len])
            self.pos += len
        else:
            res = 0
            shift = 0
            while self.data[self.pos] & 0x80:
                res |= (self.data[self.pos] & 0x7f) << (shift * 7)
                self.pos += 1
                shift += 1
            res |= self.data[self.pos] << (shift * 7)
            self.pos += 1
        return res

    def read_float(self) -> float:
        """read 4 byte to float

        args:
            len:
                0 to var int
                n to n byte

        return:
            int
        """
        self.align_to_byte()
        [res] = unpack('f', self.data[self.pos:self.pos+4])
        self.pos += 4
        return res

    def read_lit_int(self) -> int:
        """read 4 byte to int but lit

        return:
            int
        """
        self.align_to_byte()
        [res] = unpack('i', self.data[self.pos:self.pos+4])
        self.pos += 4
        return res

    def read_string(self) -> str:
        """read a string
        [1 byte for n] [n bytes to string]

        return:
            str
        """
        len = self.read_int(1)
        res = self.data[self.pos:self.pos + len].decode('utf-8', errors='ignore')
        self.pos += len
        return res

    def read_keydata(self) -> list[int]:
        """phi:GameKey data
        [1 byte for len] [1 byte for flag] [1 byte for flag 0]...

        return:
            list[int]: flag
        """
        len = self.read_int(1)
        flag = self.read_int(1)
        res = [flag >> i & 1 for i in range(5)]
        for i in range(5):
            if res[i]:
                res[i] = self.read_int(1)
        return res

    def read_record(self) -> list[dict]:
        """phi:GameRecord
        [1 byte for n] [1 byte for finish] [1 byte for fc] [4 byte to int for level 0 score] [4 byte to float for level 0 acc]...

        return:
            list[dict]: record[{"score": int, "acc": float, "fc": bool} | {}]
        """
        len = self.read_int(1)

        fns_flag = self.read_int(1)
        fc_flag = self.read_int(1)
        res = [({'score': None, 'acc': None, 'fc': bool(fc_flag & (1 << i))} if fns_flag & (1 << i) else {}) for i in range(5)]

        for i in range(5):
            if res[i]:
                res[i]['score'] = self.read_lit_int()
                res[i]['acc'] = self.read_float()
        return res

    def get_remaining(self) -> bytes:
        """bytes that are remaining

        return:
            bytes
        """
        return self.data[self.pos:]