from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum
from .tcp import TCPServer

from typing import List

class TCPPending:
    ip: str
    port: int
    init_sequence_number: int   
    
    def __init__(self, ip: str, port:int, init_sequence_number: int) -> None:
        self.ip = ip
        self.port = port
        self.init_sequence_number = init_sequence_number

class TCPManager:
    ip: str
    port: int
    tcp_connections: List[TCPServer]
    pending_connections: List[TCPPending]
    connection: Connection

    def __init__(self, connection: Connection):
        self.connection = connection

    def handle_three_way_handshake(self, message: MessageInfo):
        print(
            f"[!] [Server {message.ip}:{message.port}] Initiating three way handshake..."
        )
        segment = message.segment
        while True:
            if Segment.flag == FlagEnum.SYN_FLAG:
                self.server_seqnum = 0;
                client_seqnum = segment.sequence_number
                print(
                    f"[!] [Server {message.ip}:{message.port}] SYN received with sequence number {client_seqnum}"
                )
                self.connection.send(
                    MessageInfo(
                        message.ip,
                        message.port,
                        Segment.syn_ack_segment(sequence_number=self.server_seqnum, ack=client_seqnum + 1),
                    )
                )
                self.server_seqnum += 1
                print(
                    f"[!] [Server {message.ip}:{message.port}] SYN-ACK sent"
                )
                segment = self.connection.receive().segment
            elif Segment.flag == FlagEnum.ACK_FLAG:
                if segment.ack == self.server_seqnum + 1:
                    print(
                        f"[!] [Server {message.ip}:{message.port}] valid ACK received"
                    )
                    print(
                        f"[!] [Server {message.ip}:{message.port}] Connection established"
                    )
                    self.server_seqnum += 1
                    break
                    
                else:
                    print(
                        f"[!] [Server {message.ip}:{message.port}] invalid acknowledgemet number={segment.ack} received"
                    )
                    print(
                        f"[!] [Server {message.ip}:{message.port}] Retrying..."
                    )
                    segment = self.connection.receive().segment
            else:
                print(
                    f"[!] [Server {message.ip}:{message.port}] getting invalid flag={segment.flag}"
                )
