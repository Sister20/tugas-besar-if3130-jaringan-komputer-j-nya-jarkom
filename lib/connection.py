from socket import socket as Socket, AF_INET, SOCK_DGRAM
from .constants import TIMEOUT, SEGMENT_SIZE
from .segment import Segment

import random

class MessageInfo:
    ip: str
    port: int
    segment: Segment

    def __init__(self, ip: str, port: int, segment: Segment) -> None:
        self.ip = ip
        self.port = port
        self.segment = segment

class ControlledSocket(Socket):
    def send_random_drop(self, message: MessageInfo):
        if random.random() <= 0.2:
            print("UDP Packet loss while delivery")
        else:
            # todo make checksum invalid if needed
            self.sendto(message.segment.to_bytes(), (message.ip, message.port))

class Connection:
    socket: ControlledSocket
    ip: str
    port: int

    def __init__(
        self,
        ip: str,
        port: int,
    ) -> None:
        # initialize UDP socket
        self.socket = ControlledSocket(AF_INET, SOCK_DGRAM)
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
        self.socket.send_random_drop(message)
