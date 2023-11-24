from .connection import Connection, MessageInfo, TCPConnection
from .segment import Segment
from .constants import FlagEnum

from typing import List

# notes
# simulate a tcp connection?
# need a manager that could forward the connections

class BaseTCP:
    connection: Connection
    
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def handle_message(self, message: MessageInfo):
        raise NotImplementedError("handle_message is an abstract function that need to be implemented")
    
    def send_message(self, message: MessageInfo):
        self.connection.send(message)

class TCPSend:
    buffer: List[Segment]
    server_seqnum: int = 0

    def __init__(self, connection: Connection) -> None:
        super().__init__(connection)

    def handle_message(self, message: MessageInfo):
        pass

    def is_connected(self, ip: str, port: int) -> bool:
        for connection in self.list_TCP_connection:
            if connection.ip == ip and connection.port == port:
                return True
        return False

    def three_way_handshake(self, message: MessageInfo):
        print(
            f"[!] [Client {self.connection.ip}:{self.connection.port}] Initiating three way handshake..."
        )
        segment = message.segment
        while True:
            if Segment.flag == FlagEnum.SYN_FLAG:
                self.server_seqnum = 0;
                client_seqnum = segment.sequence_number
                print(
                    f"[!] [Client {self.connection.ip}:{self.connection.port}] SYN received with sequence number {client_seqnum}"
                )
                self.connection.send(
                    MessageInfo(
                        self.connection.ip,
                        self.connection.port,
                        Segment.syn_ack_segment(sequence_number=self.server_seqnum, ack=client_seqnum + 1),
                    )
                )
                self.server_seqnum += 1
                print(
                    f"[!] [Client {self.connection.ip}:{self.connection.port}] SYN-ACK sent"
                )
                segment = self.connection.receive().segment
            elif Segment.flag == FlagEnum.ACK_FLAG:
                if segment.ack == self.server_seqnum + 1:
                    print(
                        f"[!] [Client {self.connection.ip}:{self.connection.port}] valid ACK received"
                    )
                    print(
                        f"[!] [Client {self.connection.ip}:{self.connection.port}] Connection established"
                    )
                    self.server_seqnum += 1
                    break
                    
                else:
                    print(
                        f"[!] [Client {self.connection.ip}:{self.connection.port}] invalid acknowledgemet number={segment.ack} received"
                    )
                    print(
                        f"[!] [Client {self.connection.ip}:{self.connection.port}] Retrying..."
                    )
                    segment = self.connection.receive().segment
            else:
                print(
                    f"[!] [Client {self.connection.ip}:{self.connection.port}] getting invalid flag={segment.flag}"
                )