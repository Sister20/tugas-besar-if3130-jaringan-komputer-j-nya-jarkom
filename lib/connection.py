from socket import socket as Socket, AF_INET, SOCK_DGRAM, timeout as socket_timeout
from .constants import TIMEOUT, SEGMENT_SIZE
from .segment import Segment, InvalidChecksumException

import random
import logging

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
    ) -> None:
        # initialize UDP socket
        self.socket = Socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def listen(self):
        self.socket.bind((self.ip, self.port))
        logging.info(f"Socket started at {self.ip}:{self.port}")

    def close(self):
        self.socket.close()

    def receive(self, timeout: int = TIMEOUT) -> MessageInfo:
        self.socket.settimeout(timeout)
        [payload, source] =  self.socket.recvfrom(SEGMENT_SIZE)
        [host, port] = source

        try:
            segment = Segment.from_bytes(payload)
        except InvalidChecksumException:
            logging.info(f"from {host}:{port} received invalid packet. dropping ...")
            raise socket_timeout

        logging.info(f"from {host}:{port} received {segment.flag} packet with seqnum {segment.sequence_number} and ack {segment.ack}")

        return MessageInfo(host, port, segment)
    
    def send(self, message: MessageInfo):
        logging.info(f"Sending {message.segment.flag} packet to {message.ip}:{message.port} with seqnum {message.segment.sequence_number} and ack {message.segment.ack}")
        self.socket.sendto(message.segment.to_bytes(), (message.ip, message.port))
