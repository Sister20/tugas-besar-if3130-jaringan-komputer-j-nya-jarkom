from pathlib import Path
import struct
from typing import List, Tuple

class Metadata:
    filename_bytes_length: int
    extension_bytes_length: int
    filename: str
    extension: str

    def __init__(self,
                 path: str) -> None:  
        self.path = path
        self.filename = Path(path).stem
        if not (0 < len(self.filename) < 100):
            raise NameError("Filename length must be between 1 and 100 characters")
        self.extension = Path(path).suffix
        if not (0 < len(self.extension) < 10):
            raise NameError("Extension length must be between 1 and 10 characters")
        self.filename_bytes_length = len(self.filename.encode("utf-8"))
        self.extension_bytes_length = len(self.extension.encode("utf-8"))


    def __str__(self) -> str:
        result = f"{'seqnum':12}\t\t| {self.sequence_number}\n"
        result += f"{'acknum':12}\t\t| {self.ack}\n"
        result += f"{'flag-syn':12}\t\t| {self.flag.syn >> 1}\n"
        result += f"{'flag-ack':12}\t\t| {self.flag.ack >> 4}\n"
        result += f"{'flag-fin':12}\t\t| {self.flag.fin}\n"
        result += f"{'checksum':24}| {self.checksum}\n"
        result += f"{'data-size':24}| {len(self.data)}\n"

        return result

    def to_bytes(self) -> bytes:
        result = b""
        result += struct.pack("<I", self.filename_bytes_length)
        result += struct.pack("<I", self.extension_bytes_length)
        result += self.filename.encode("utf-8")
        result += self.extension.encode("utf-8")

        return result

    @staticmethod
    def get_metadata(src: bytes) -> Tuple[str, str]:
        filename_bytes_length = struct.unpack("<I", src[0:4])[0]
        extension_bytes_length = struct.unpack("<I", src[4:8])[0]
        filename = src[8:8+filename_bytes_length].decode("utf-8")
        extension = src[8+filename_bytes_length:8+filename_bytes_length+extension_bytes_length].decode("utf-8")

        return (filename, extension)