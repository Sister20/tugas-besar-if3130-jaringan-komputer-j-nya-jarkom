class Segment:
    def to_bytes(self) -> bytes:
        return bytearray([1, 2, 4])

    @staticmethod
    def from_bytes(src: bytes) -> 'Segment':
        return Segment()