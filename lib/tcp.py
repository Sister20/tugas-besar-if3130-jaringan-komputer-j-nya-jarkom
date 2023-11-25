import random

from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum

from typing import List
from enum import Enum

# notes
# simulate a tcp connection?
# need a manager that could forward the connections

class TCPStatusEnum(Enum):
    UNINITIALIZED = 0
    WAITING_SYN_ACK = 1
    WAITING_ACK = 2
    ESTABLISHED = 3

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

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)

    def connect(self):
        while self.status != TCPStatusEnum.ESTABLISHED:
            try:
                if self.status == TCPStatusEnum.UNINITIALIZED:
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.syn_segment(random.randint(0, 4294967000))))
                    message = self.connection.receive(10)

                if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                    pass
            except TimeoutError:
                pass

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

    