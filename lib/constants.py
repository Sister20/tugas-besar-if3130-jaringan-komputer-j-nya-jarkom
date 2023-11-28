from enum import Enum

DEFAULT_IP = "127.0.0.1"
DEFAULT_CLIENT_PORT = 3000
DEFAULT_BROADCAST_PORT = 8000
TIMEOUT = 2
HEADER_SIZE = 12
SEGMENT_SIZE = 32768
PAYLOAD_SIZE = SEGMENT_SIZE - HEADER_SIZE

class FlagEnum(Enum):
    NO_FLAG: int = 0b0 # type: ignore
    SYN_FLAG: int = 0b000000010 # type: ignore # 2
    ACK_FLAG: int = 0b000010000 # type: ignore # 16
    FIN_FLAG: int = 0b000000001 # type: ignore # 1
    SYN_ACK_FLAG: int = SYN_FLAG | ACK_FLAG # type: ignore
    FIN_ACK_FLAG: int = FIN_FLAG | ACK_FLAG # type: ignore

    def __int__(self) -> int:
        return self.value