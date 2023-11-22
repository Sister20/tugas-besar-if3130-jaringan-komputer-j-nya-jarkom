from socket import socket as Socket, AF_INET, SOCK_DGRAM, timeout as SocketTimeout
from .constants import TIMEOUT, SEGMENT_SIZE
from .Segment import Segment
from typing import Tuple

class Connection:
    socket: Socket
    ip: str
    port: int

    def __init__(
        self,
        ip: str,
        port: int,
        socket: Socket
    ) -> None:
        # initialize UDP socket
        self.socket = Socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        print(f"[i] Socket started at {self.ip}:{self.port}")

    def close(self):
        self.socket.close()

    def receive(self, timeout: int = TIMEOUT) -> Tuple[str, Segment]:
        self.socket.settimeout(timeout)
        [payload, source] =  self.socket.recvfrom(SEGMENT_SIZE)

        return (source, Segment.from_bytes(payload))
    
    def send(self, payload: Segment, destination: Tuple[str, int]):
        self.socket.sendto(payload.to_bytes(), destination)