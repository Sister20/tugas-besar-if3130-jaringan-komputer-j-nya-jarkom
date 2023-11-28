import struct

from .constants import FlagEnum
from .checksum import calculate_checksum
from .hamming import Hamming

from typing import List


class InvalidChecksumException(Exception):
    pass


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
        return struct.pack("<B", self.syn | self.ack | self.fin)

    def __str__(self) -> str:
        if self.syn and self.ack:
            return "SYN-ACK"
        elif self.fin and self.ack:
            return "FIN-ACK"
        elif self.syn:
            return "SYN"
        elif self.fin:
            return "FIN"
        elif self.ack:
            return "ACK"

        return "DATA"

    def __eq__(self, __value: object) -> bool:
        if (isinstance(__value, int)):
            return self.flag == __value
        elif isinstance(__value, FlagEnum):
            return self.flag == int(__value)
        elif isinstance(__value, SegmentFlag):
            return self.flag == __value.flag

        return False


class Segment:
    sequence_number: int
    ack: int
    flag: SegmentFlag
    checksum: int
    data: bytes

    def __init__(self,
                 sequence_number: int = 0,
                 ack: int = 0,
                 flag: SegmentFlag = SegmentFlag(0b0),
                 checksum: int = 0,
                 data: bytes = b"") -> None:
        self.sequence_number = sequence_number
        self.ack = ack
        self.flag = flag
        self.checksum = checksum
        self.data = data

    def __str__(self) -> str:
        result = f"{'seqnum':12}\t\t| {self.sequence_number}\n"
        result += f"{'acknum':12}\t\t| {self.ack}\n"
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
        checksum = calculate_checksum(self._get_bytes_for_checksum())

        result = b""
        result += struct.pack("<I", self.sequence_number)
        result += struct.pack("<I", self.ack)
        result += self.flag.to_bytes()
        result += struct.pack("<x")
        result += struct.pack("<H", checksum)
        result += self.data
        hamming = Hamming()
        result = hamming.encode(result)

        return result

    def is_valid(self) -> bool:
        return calculate_checksum(self._get_bytes_for_checksum()) == self.checksum

    def _get_bytes_for_checksum(self) -> bytes:
        result = b""
        result += struct.pack("<I", self.sequence_number)
        result += struct.pack("<I", self.ack)
        result += self.flag.to_bytes()
        result += self.data

        return result

    @staticmethod
    def from_bytes(src: bytes) -> 'Segment':
        hamming = Hamming()
        src = hamming.decode(src)

        sequence_number = struct.unpack("<I", src[0:4])[0]
        ack = struct.unpack("<I", src[4:8])[0]
        flag = SegmentFlag(struct.unpack("<B", src[8:9])[0])
        checksum = struct.unpack("<H", src[10:12])[0]
        data = b"" if len(src) == 12 else src[12:]

        segment = Segment(
            sequence_number,
            ack,
            flag,
            checksum,
            data
        )

        if not segment.is_valid():
            raise InvalidChecksumException()

        return segment

    @staticmethod
    def syn_segment(sequence_number: int) -> 'Segment':
        return Segment(
            sequence_number=sequence_number,
            flag=SegmentFlag(int(FlagEnum.SYN_FLAG))
        )

    @staticmethod
    def ack_segment(sequence_number: int, ack: int) -> 'Segment':
        return Segment(
            sequence_number=sequence_number,
            ack=ack,
            flag=SegmentFlag(int(FlagEnum.ACK_FLAG))
        )

    @staticmethod
    def syn_ack_segment(sequence_number: int, ack: int) -> 'Segment':
        return Segment(
            sequence_number=sequence_number,
            ack=ack,
            flag=SegmentFlag(int(FlagEnum.SYN_ACK_FLAG))
        )

    @staticmethod
    def fin_segment(sequence_number: int) -> 'Segment':
        return Segment(
            sequence_number=sequence_number,
            flag=SegmentFlag(int(FlagEnum.FIN_FLAG))
        )

    @staticmethod
    def fin_ack_segment(sequence_number: int, ack: int) -> 'Segment':
        return Segment(
            sequence_number=sequence_number,
            ack=ack,
            flag=SegmentFlag(int(FlagEnum.FIN_ACK_FLAG))
        )

    @staticmethod
    def data_segment(data: bytes) -> 'Segment':
        return Segment(
            data=data,
            flag=SegmentFlag(0)
        )
