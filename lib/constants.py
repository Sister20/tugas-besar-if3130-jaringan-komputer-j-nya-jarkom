from enum import Enum

DEFAULT_IP = "127.0.0.1"
DEFAULT_CLIENT_PORT = 3000
DEFAULT_BROADCAST_PORT = 8000
TIMEOUT = 5
SEGMENT_SIZE = 32764

class FlagEnum(Enum):
    SYN_FLAG: int = 0b000000010 # 2
    ACK_FLAG: int = 0b000010000 # 16
    FIN_FLAG: int = 0b000000001 # 1
    SYN_ACK_FLAG: int = SYN_FLAG | ACK_FLAG
    FIN_ACK_FLAG: int = FIN_FLAG | ACK_FLAG

    def __int__(self) -> int:
        return self.value