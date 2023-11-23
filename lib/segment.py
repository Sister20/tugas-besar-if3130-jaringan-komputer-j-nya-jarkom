import struct
from .constants import FlagEnum
from .checksum import calculate_checksum
from typing import List

class SegmentFlag:
    syn: int
    ack: int
    fin: int
    flag: int

    def __init__(self, flag: int) -> None:
        self.syn = flag & int(FlagEnum.SYN_FLAG)
        self.ack = flag & int(FlagEnum.ACK_FLAG)
        self.fin = flag & int(FlagEnum.FIN_FLAG)
        self.flag = self.syn | self.ack | self.fin

    def to_bytes(self) -> bytes:
        return struct.pack("B", self.syn | self.ack | self.fin)
    
    def __str__(self) -> str:
        return bin(self.flag)


class Segment:
    sequence_number: int
    ack: int
    flag: SegmentFlag
    checksum: int
    data: bytes

    def __init__(self,
                 seqnum: int = 0,
                 ack: int = 0,
                 flag: SegmentFlag = SegmentFlag(0b0),
                 checksum: int = 0,
                 data: bytes = b"") -> None:
        self.sequence_number = seqnum
        self.ack = ack
        self.flag = flag
        self.checksum = checksum
        self.data = data

    def __str__(self) -> str:
        result = f"{'seqnum': 12}\t\t{self.sequence_number}\n"
        result += f"{'acknum': 12}\t\t{self.ack}\n"
        result += f"{'flag-syn':12}\t\t| {self.flag.syn >> 1}\n"
        result += f"{'flag-ack':12}\t\t| {self.flag.ack >> 4}\n"
        result += f"{'flag-fin':12}\t\t| {self.flag.fin}\n"
        result += f"{'checksum':24}| {self.checksum}\n"
        result += f"{'data-size':24}| {len(self.data)}\n"

        return result

    def set_flag(self, flags: List[FlagEnum]):
        flag = 0b0

        for value in flags:
            flag |= int(value)

        self.flag = SegmentFlag(flag)

    def to_bytes(self) -> bytes:
        checksum = calculate_checksum(self.data)

        result = b""
        result += struct.pack("I", self.sequence_number)
        result += struct.pack("I", self.ack)
        result += self.flag.to_bytes()
        result += struct.pack("x")
        result += struct.pack("H", self.checksum)
        result += self.data

        return result

    @staticmethod
    def from_bytes(src: bytes) -> 'Segment':
        sequence_number = struct.unpack("I", src[0:4])[0]
        ack = struct.unpack("I", src[4:8])[0]
        flag = SegmentFlag(struct.unpack("B", src[8:9])[0])
        checksum = struct.unpack("H", src[10:12])[0]
        data = src[12:]

        return Segment(
            sequence_number,
            ack,
            flag,
            checksum,
            data
        )