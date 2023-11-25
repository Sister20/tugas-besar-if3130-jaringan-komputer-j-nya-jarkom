import os
import math
from io import BufferedReader, BufferedWriter
from .constants import SEGMENT_SIZE

class FilePayload:
    path: str
    chunk_size: int
    filesize: int
    total_chunk: int
    fd: BufferedReader
    
    def __init__(self, path: str, chunk_size: int = SEGMENT_SIZE):
        self.path = path
        self.chunk_size = chunk_size
        
        stats = os.stat(path)
        self.filesize = stats.st_size
        self.total_chunk = math.ceil(self.filesize/self.chunk_size)

        self.fd = open(path, "rb")

    def get_chunk(self, chunk_number: int) -> bytes:
        if (chunk_number < 1 or chunk_number > self.total_chunk):
            raise Exception("Invalid chunk number")
        
        offset = (chunk_number - 1) * self.chunk_size
        self.fd.seek(offset)

        return self.fd.read(self.chunk_size)
    
    def __del__(self):
        if (not self.fd.closed):
            self.fd.close()

class FileBuilder:
    path: str
    filesize: int
    bytes_written: int
    fd: BufferedWriter

    def __init__(self, path: str, filesize: int):
        self.bytes_written = 0
        self.path = path
        self.filesize = filesize

        self.fd = open(path, "wb")

    def write(self, data: bytes):
        if self.bytes_written == self.filesize:
            raise Exception("File already written completely")

        self.bytes_written += len(data)
        self.fd.write(data)

        if self.bytes_written > self.filesize:
            raise Exception(f"Written data {self.bytes_written} bytes are more than expected {self.filesize} bytes")
        elif self.bytes_written == self.filesize:
            # auto close if file written successfully
            self.fd.close()

    def is_completed(self) -> bool:
        return self.bytes_written == self.filesize

    def __del__(self):
        if (not self.fd.closed):
            self.fd.close()