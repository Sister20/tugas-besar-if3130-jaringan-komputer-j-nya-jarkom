from socket import socket as Socket, AF_INET, SOCK_DGRAM
from .constants import TIMEOUT, SEGMENT_SIZE
from .segment import Segment

class MessageInfo:
    ip: str
    port: int
    segment: Segment

    def __init__(self, ip: str, port: int, segment: Segment) -> None:
        self.ip = ip
        self.port = port
        self.segment = segment

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

    def receive(self, timeout: int = TIMEOUT) -> MessageInfo:
        self.socket.settimeout(timeout)
        [payload, source] =  self.socket.recvfrom(SEGMENT_SIZE)
        [host, port] = source

        return MessageInfo(host, port, Segment.from_bytes(payload))
    
    def send(self, message: MessageInfo):
        self.socket.sendto(message.segment.to_bytes(), (message.ip, message.port))