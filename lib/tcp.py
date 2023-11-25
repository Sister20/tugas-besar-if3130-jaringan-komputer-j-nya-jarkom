import random

from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum

from enum import Enum

class TCPStatusEnum(Enum):
    UNINITIALIZED = 0
    WAITING_SYN_ACK = 1
    WAITING_ACK = 2
    WAITING_FIRST_PACKET = 3
    ESTABLISHED = 4

class BaseTCP:
    ip: str # IP and Port of the lawan bicara
    port: int 
    connection: Connection
    
    status: TCPStatusEnum
    
    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection = connection
        self.status = TCPStatusEnum.UNINITIALIZED

    def handle_message(self, message: MessageInfo):
        raise NotImplementedError("handle_message is an abstract function that need to be implemented")

class TCPClient(BaseTCP):
    handshake_sequence_number: int = 0

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)

    def connect(self, init=True):
        if init:
            print(f"[!] [Client] Initiating Three Way Handshake")

        while self.status != TCPStatusEnum.ESTABLISHED:
            try:
                if self.status == TCPStatusEnum.UNINITIALIZED:
                    self.handshake_sequence_number = random.randint(0, 4294967000)

                    self.connection.send(MessageInfo(self.ip, self.port, Segment.syn_segment(self.handshake_sequence_number)))
                    print(f"[!] [Client] Sending SYN packet")
                    message = self.connection.receive(10)
                    self.status = TCPStatusEnum.WAITING_SYN_ACK

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        print(f"[!] [Client] Received SYN-ACK. Sending ACK")
                        
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                        else:
                            print(f"[!] [Client] Invalid ack number. Dropping ...")
                    else:
                        print(f"[!] [Client] Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_SYN_ACK:
                    message = self.connection.receive(10)

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        print(f"[!] [Client] Received SYN-ACK. Sending ACK")

                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                            break
                        else:
                            print(f"[!] [Client] Invalid ack number. Dropping ...")
                    else:
                        print(f"[!] [Client] Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET:
                    print(f"[!] [Client] Received SYN-ACK. Sending ACK")
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                    break

            except TimeoutError:
                print(f"[!] [Client] Timeout error during phase {self.status} ... will retrying")
                pass

    def handle_message(self, message: MessageInfo):
        # first packet received
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag != FlagEnum.SYN_ACK_FLAG:
            self.status = TCPStatusEnum.ESTABLISHED
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            print(f"[!] [Client] Received SYN-ACK. Sending ACK")
            if message.segment.ack == self.handshake_sequence_number + 1:
                self.connect(False)
            else:
                print(f"[!] [Client] Invalid ack number. Dropping ...")
        else:
            print(f"[!] [Client] Received a packet")


class TCPServer(BaseTCP):
    ver_seqnum: int = 0

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)

    def begin_file_transfer(self):
        print(
            f"[!] [Server {self.ip}:{self.port}] Beginning file transfer..."
        )   
        pass

    def handle_message(self, message: MessageInfo):
        pass

    