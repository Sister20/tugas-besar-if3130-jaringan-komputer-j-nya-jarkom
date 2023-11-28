from mimetypes import init
from .connection import MessageInfo, Connection
from .segment import FlagEnum
from .segment import Segment
from .tcp import TCPClient, TCPStatusEnum, TCPServer
from .segment_sender import SenderBuffer
import logging
from .metadata import Metadata
from os import path

class FileReceiver(TCPClient):
    def __init__(self, connection: Connection, ip: str, port: int, file_path: str) -> None:
        super().__init__(connection, ip, port)
        self.file_path = file_path
        self.file_size_bytes = 0
        self.file_data = b""  # Buffer
        self.is_metadata_received = False
        self.is_file_received = False

    def handle_message(self, message: MessageInfo):
        # initial three-way handshake
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            super().handle_message(message)
            return

        # data transfer
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            super().handle_message(message)
            self.handle_data(message.segment)

        elif self.status == TCPStatusEnum.ESTABLISHED and message.segment.flag == FlagEnum.NO_FLAG:
            self.handle_data(message.segment)

        # other is closing the connection
        elif self.status == TCPStatusEnum.CLOSE_WAIT and message.segment.flag == FlagEnum.FIN_FLAG:
            self.close()
            return

    def handle_data(self, segment: Segment):
        if self.is_file_received:
            logging.info("File already received")
            return
        if segment.sequence_number == self.server_sequence_number and segment.is_valid():

            if not self.is_metadata_received:
                self._handle_metadata(segment)
                self.is_metadata_received = True
                return
            
            self.file_data += segment.data

            self.server_sequence_number += 1

            # send ACK for the received segment
            ack_segment = Segment.ack_segment(0, segment.sequence_number + 1)
            self.connection.send(MessageInfo(self.ip, self.port, ack_segment))

            if len(self.file_data) >= self.file_size_bytes:
                self.write_to_file()
                self.is_file_received = True
        elif segment.sequence_number < self.server_sequence_number:
            ack_segment = Segment.ack_segment(0, self.server_sequence_number)
            self.connection.send(MessageInfo(self.ip, self.port, ack_segment))
        else:
            logging.info(f"Ignoring out-of-order or invalid segment with sequence number {segment.sequence_number}")

    def _handle_metadata(self, segment: Segment):
        (filename, extension, file_size_bytes) = Metadata.get_metadata(segment.data)
        self.file_size_bytes = file_size_bytes
        self.server_sequence_number += 1

        self.file_path = path.join(self.file_path, filename + extension)

        # send ACK for the received segment
        ack_segment = Segment.ack_segment(0, segment.sequence_number + 1)
        self.connection.send(MessageInfo(self.ip, self.port, ack_segment))

    def write_to_file(self):
        with open(self.file_path, "wb") as file:
            file.write(self.file_data)

        logging.info(f"File received and saved at: {self.file_path}")
        
class FileSender(TCPServer):
    sender_buffer: SenderBuffer
    receiver_ack_number: int

    def __init__(self, filePath: str, connection: Connection, ip: str, port: int, ack_number: int) -> None:
        super().__init__(connection, ip, port)
        self.receiver_ack_number = ack_number
        self.sender_buffer = SenderBuffer(connection, ip, port, filePath, ack_number)

    def begin_transfer(self):
        self.sender_buffer.send(self.receiver_ack_number)

    def handle_message(self, message: MessageInfo):
        self.sender_buffer.send(message.segment.ack)