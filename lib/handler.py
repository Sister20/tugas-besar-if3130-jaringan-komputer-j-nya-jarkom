from mimetypes import init
from .connection import MessageInfo, Connection
from .segment import FlagEnum
from .tcp import TCPClient, TCPStatusEnum, TCPServer
from .segment_sender import SenderBuffer
import logging

class FileReceiver(TCPClient):
    def handle_message(self, message: MessageInfo):
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            super().handle_message(message)
            return
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            # called but not returned
            super().handle_message(message)
        # todo add condition if closing connection and pass to parent class

        # handle file here
        
class FileSender(TCPServer):
    sender_buffer: SenderBuffer
    receiver_ack_number: int

    def __init__(self, filePath: str, connection: Connection, ip: str, port: int, ack_number: int) -> None:
        super().__init__(connection, ip, port)
        self.receiver_ack_number = ack_number
        self.sender_buffer = SenderBuffer(connection, ip, port, filePath, ack_number)

    def begin_transfer(self):
        print("Begin tranfsfer")
        self.sender_buffer.send(self.receiver_ack_number)

    def handle_message(self, message: MessageInfo):
        self.sender_buffer.send(message.segment.ack)